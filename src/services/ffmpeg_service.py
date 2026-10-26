"""FFmpeg service for video and audio processing."""
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from ..utils.logger import setup_logger
from ..utils.config import config
from ..models.video_metadata import VideoMetadata, AudioTrack


logger = setup_logger(__name__)


class FFmpegService:
    """FFmpeg wrapper for video and audio operations."""
    
    def __init__(self, ffmpeg_path: str = None, ffprobe_path: str = None):
        self.ffmpeg_path = ffmpeg_path or config.ffmpeg_path
        self.ffprobe_path = ffprobe_path or config.ffprobe_path
        self._validate_ffmpeg()
    
    def _validate_ffmpeg(self) -> None:
        """Check if FFmpeg and FFprobe are available."""
        try:
            subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                check=True,
                timeout=10
            )
            subprocess.run(
                [self.ffprobe_path, '-version'],
                capture_output=True,
                check=True,
                timeout=10
            )
            logger.info("FFmpeg and FFprobe validated successfully")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"FFmpeg validation failed: {e}")
            raise RuntimeError("FFmpeg or FFprobe not found. Please install FFmpeg.") from e
    
    def get_video_info(self, video_path: str) -> VideoMetadata:
        """Extract video metadata using FFprobe."""
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            data = json.loads(result.stdout)
            
            # Extract video stream
            video_stream = next(
                (s for s in data['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # Extract audio streams
            audio_tracks = []
            for idx, stream in enumerate(data['streams']):
                if stream['codec_type'] == 'audio':
                    audio_tracks.append(AudioTrack(
                        index=idx,
                        codec=stream.get('codec_name', 'unknown'),
                        sample_rate=int(stream.get('sample_rate', 0)),
                        channels=int(stream.get('channels', 0)),
                        language=stream.get('tags', {}).get('language')
                    ))
            
            # Calculate FPS
            fps_str = video_stream.get('r_frame_rate', '0/1')
            fps_parts = fps_str.split('/')
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 0.0
            
            metadata = VideoMetadata(
                filepath=video_path,
                duration=float(data['format'].get('duration', 0)),
                width=int(video_stream.get('width', 0)),
                height=int(video_stream.get('height', 0)),
                fps=fps,
                video_codec=video_stream.get('codec_name', 'unknown'),
                audio_tracks=audio_tracks,
                format_name=data['format'].get('format_name', 'unknown'),
                bitrate=int(data['format'].get('bit_rate', 0)) if data['format'].get('bit_rate') else None
            )
            
            logger.info(f"Extracted metadata for {video_path}: {metadata.resolution} @ {metadata.fps}fps")
            return metadata
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFprobe failed: {e.stderr}")
            raise RuntimeError(f"Failed to extract video info: {e.stderr}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse FFprobe output: {e}")
            raise RuntimeError("Invalid FFprobe output") from e
    
    def extract_audio(self, video_path: str, output_path: str, 
                     audio_track: int = 0) -> str:
        """Extract audio from video without re-encoding."""
        try:
            output_path = str(Path(output_path).with_suffix('.wav'))
            
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-map', f'0:a:{audio_track}',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                output_path
            ]
            
            logger.info(f"Extracting audio from {video_path} to {output_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=600
            )
            
            if not Path(output_path).exists():
                raise RuntimeError("Audio extraction failed: output file not created")
            
            logger.info(f"Audio extracted successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg audio extraction failed: {e.stderr}")
            raise RuntimeError(f"Audio extraction failed: {e.stderr}") from e
    
    def merge_audio_video(self, video_path: str, audio_path: str, 
                         output_path: str, original_audio_volume: float = 0.1) -> str:
        """Merge new audio with video, preserving video stream."""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-filter_complex',
                f'[0:a]volume={original_audio_volume}[a1];[1:a]volume=1.0[a2];[a1][a2]amix=inputs=2:duration=longest[aout]',
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', config.audio_codec,
                '-b:a', config.audio_bitrate,
                '-shortest',
                '-y',
                output_path
            ]
            
            logger.info(f"Merging audio and video to {output_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=1800
            )
            
            if not Path(output_path).exists():
                raise RuntimeError("Video merge failed: output file not created")
            
            logger.info(f"Video merged successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg merge failed: {e.stderr}")
            raise RuntimeError(f"Video merge failed: {e.stderr}") from e
    
    def replace_audio(self, video_path: str, audio_path: str, 
                     output_path: str) -> str:
        """Replace video audio entirely, preserving video stream."""
        try:
            # Use faster encoding settings to reduce disk I/O
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'copy',  # Copy video without re-encoding
                '-c:a', 'aac',   # Use AAC for compatibility
                '-b:a', '128k',
                '-preset', 'ultrafast',  # Fastest encoding preset
                '-threads', '0',  # Use all CPU threads
                '-shortest',
                '-y',
                output_path
            ]
            
            logger.info(f"Replacing audio in {video_path} with {audio_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=1800
            )
            
            if not Path(output_path).exists():
                raise RuntimeError("Audio replacement failed: output file not created")
            
            logger.info(f"Audio replaced successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg audio replacement failed: {e.stderr}")
            raise RuntimeError(f"Audio replacement failed: {e.stderr}") from e
    
    def concatenate_audio(self, audio_files: List[str], output_path: str) -> str:
        """Concatenate multiple audio files."""
        try:
            # Create concat file list
            concat_file = Path(config.temp_dir) / 'concat_list.txt'
            with open(concat_file, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    f.write(f"file '{Path(audio_file).absolute()}'\n")
            
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            logger.info(f"Concatenating {len(audio_files)} audio files")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            
            if not Path(output_path).exists():
                raise RuntimeError("Audio concatenation failed: output file not created")
            
            logger.info(f"Audio concatenated successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg concatenation failed: {e.stderr}")
            raise RuntimeError(f"Audio concatenation failed: {e.stderr}") from e
        finally:
            # Clean up concat file
            if concat_file.exists():
                concat_file.unlink()
    
    def compose_audio_timeline(self, segments: List, output_path: str, total_duration: float) -> str:
        """Compose audio from segments at their exact timestamps with speed adjustment.
        
        Args:
            segments: List of DialogueSegment objects with start_time, end_time, and audio_path
            output_path: Path for the output audio file
            total_duration: Total duration of the video in seconds
        """
        try:
            valid_segments = [s for s in segments if s.audio_path and Path(s.audio_path).exists()]
            
            if not valid_segments:
                raise RuntimeError("No valid audio segments to compose")
            
            logger.info(f"Composing audio timeline from {len(valid_segments)} segments")
            
            # Split segments into batches to balance performance
            batch_size = 15
            batches = [valid_segments[i:i+batch_size] for i in range(0, len(valid_segments), batch_size)]
            
            temp_dir = Path(config.temp_dir) / "audio_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            batch_files = []
            
            # Process each batch
            for batch_idx, batch in enumerate(batches):
                inputs = []
                filter_parts = []
                
                # Add silent base for this batch
                inputs.extend(['-f', 'lavfi', '-t', str(total_duration), '-i', 'anullsrc=r=48000:cl=stereo'])
                
                # Add all segments in this batch
                for i, segment in enumerate(batch):
                    inputs.extend(['-i', str(segment.audio_path)])
                    delay_ms = int(segment.start_time * 1000)
                    filter_parts.append(f"[{i+1}]adelay={delay_ms}|{delay_ms}[a{i}]")
                
                # Mix base with all delayed segments
                mix_inputs = '[0]' + ''.join([f"[a{i}]" for i in range(len(batch))])
                filter_parts.append(f"{mix_inputs}amix=inputs={len(batch)+1}:duration=first:dropout_transition=0")
                
                filter_complex = ';'.join(filter_parts)
                
                # Use compressed format (MP3) to reduce disk I/O
                batch_output = temp_dir / f"b{batch_idx}.mp3"
                
                cmd = [self.ffmpeg_path]
                cmd.extend(inputs)
                cmd.extend([
                    '-filter_complex', filter_complex,
                    '-ar', '48000',
                    '-ac', '2',
                    '-b:a', '192k',  # Compressed audio to reduce file size
                    '-t', str(total_duration),
                    '-y',
                    str(batch_output)
                ])
                
                logger.info(f"Processing batch {batch_idx + 1}/{len(batches)} - this may take a moment...")
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
                batch_files.append(str(batch_output))
            
            # Mix all batch outputs
            if len(batch_files) == 1:
                # Only one batch, convert to final format
                cmd = [
                    self.ffmpeg_path,
                    '-i', batch_files[0],
                    '-ar', '48000',
                    '-ac', '2',
                    '-y',
                    output_path
                ]
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
            else:
                # Mix batches
                inputs = []
                for bf in batch_files:
                    inputs.extend(['-i', bf])
                
                filter_str = f'amix=inputs={len(batch_files)}:duration=first:dropout_transition=0'
                
                cmd = [self.ffmpeg_path]
                cmd.extend(inputs)
                cmd.extend([
                    '-filter_complex', filter_str,
                    '-ar', '48000',
                    '-ac', '2',
                    '-y',
                    output_path
                ])
                
                logger.info(f"Mixing {len(batch_files)} batches - final step...")
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
            
            if not Path(output_path).exists():
                raise RuntimeError("Audio composition failed: output file not created")
            
            # Clean up temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            logger.info(f"Audio timeline composed successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg timeline composition failed: {e.stderr}")
            raise RuntimeError(f"Audio timeline composition failed: {e.stderr}") from e
        except Exception as e:
            logger.error(f"Audio composition error: {e}")
            raise
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of an audio file in seconds."""
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            return float(result.stdout.strip())
            
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"Could not get audio duration for {audio_path}: {e}")
            return 0.0
