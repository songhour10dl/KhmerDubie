# KhmerDub Studio - Kiri TTS API Documentation

## Important: Kiri TTS API Verification Required

The current TTS implementation in `src/services/tts_service.py` is a **placeholder** based on common TTS API patterns. Before using Kiri TTS in production, you must verify the actual API specification.

---

## What Needs Verification

1. **Base URL**
   - Current placeholder: `https://api.kiri.ai/v1`
   - Verify actual endpoint from Kiri documentation

2. **Authentication**
   - Current: Bearer token in Authorization header
   - Verify: API key format and header requirements

3. **Request Format**
   ```json
   {
     "text": "សួស្តី",
     "voice": "khmer_female_1",
     "language": "km",
     "format": "wav",
     "sample_rate": 48000
   }
   ```
   Verify: Actual JSON structure, required fields, optional parameters

4. **Response Format**
   - Current: Expects raw audio binary in response body
   - Verify: Response structure (direct audio or JSON with URL?)

5. **Available Voices**
   - Current placeholder: "khmer_female_1"
   - Verify: Actual Khmer voice IDs from provider

6. **Endpoints**
   - TTS Generation: `/tts` (verify actual path)
   - Voice Listing: `/voices` (verify actual path)
   - Test/Health: Not implemented (check if available)

---

## How to Verify

1. **Get Official Documentation**
   - Contact Kiri support for API documentation
   - Request developer access and API examples
   - Review any SDKs or client libraries

2. **Test API Manually**
   Use PowerShell to test requests:
   ```powershell
   $headers = @{
       "Authorization" = "Bearer YOUR_API_KEY"
       "Content-Type" = "application/json"
   }
   
   $body = @{
       text = "សួស្តី"
       voice = "khmer_female_1"
       language = "km"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "https://api.kiri.ai/v1/tts" -Method Post -Headers $headers -Body $body -OutFile "test.wav"
   ```

3. **Update Implementation**
   Modify `src/services/tts_service.py` based on actual API:
   - Update `_synthesize_kiri()` method
   - Update `_test_kiri_connection()` method
   - Update `_get_kiri_voices()` method
   - Update request/response handling

---

## Alternative: Other Khmer TTS Providers

If Kiri TTS is not available or doesn't support Khmer, consider:

1. **Google Cloud Text-to-Speech**
   - Check Khmer (km) language support
   - Well-documented API
   - Pay-per-use pricing

2. **Microsoft Azure Text-to-Speech**
   - Check Khmer language support
   - REST API well-documented
   - Neural voices available

3. **ElevenLabs**
   - Voice cloning for custom Khmer voices
   - REST API available
   - High quality but more expensive

4. **Local TTS Engines**
   - eSpeak-ng (basic Khmer support)
   - Piper TTS (if Khmer models available)
   - Lower quality but no API costs

---

## Implementing a New Provider

To add a new TTS provider:

1. **Extend TTSService class** in `src/services/tts_service.py`:
   ```python
   def _synthesize_new_provider(self, text: str, output_path: str, voice: str) -> str:
       # Implement provider-specific logic
       pass
   ```

2. **Add provider selection** in `synthesize()` method:
   ```python
   if self.provider == "new_provider":
       return self._synthesize_new_provider(text, output_path, voice)
   ```

3. **Update Settings Dialog** in `src/ui/settings_dialog.py`:
   ```python
   self.tts_provider.addItems(["kiri", "new_provider"])
   ```

4. **Update `.env.example`** with new provider settings

5. **Test thoroughly** with Khmer text

---

## Current Implementation Status

✅ **Implemented (needs verification)**:
- Basic TTS service structure
- Kiri API placeholder
- Voice selection interface
- Error handling
- Connection testing

❌ **Not Yet Verified**:
- Actual Kiri API endpoint
- Real API request/response format
- Available Khmer voices
- Rate limits and pricing
- Audio format options

---

## Testing Checklist

Before marking TTS as production-ready:

- [ ] Obtain official Kiri API documentation
- [ ] Verify base URL endpoint
- [ ] Test authentication method
- [ ] Confirm request JSON structure
- [ ] Verify response format (binary audio or JSON?)
- [ ] Test with simple Khmer text
- [ ] Test with complex Khmer text (sentences, paragraphs)
- [ ] Verify audio quality and sample rate
- [ ] Test error responses (invalid key, quota exceeded)
- [ ] Confirm voice IDs for Khmer
- [ ] Test voice listing endpoint
- [ ] Document rate limits
- [ ] Document pricing/credits

---

## Contact Information

For Kiri TTS API access:
- Website: [https://kiri.ai](https://kiri.ai) (verify actual URL)
- Support: Check website for contact information
- Documentation: Request developer documentation

---

**Note**: Until the Kiri TTS API is verified, the TTS functionality will fail with API errors. The rest of the application (import, transcription, translation, video processing) works independently and can be tested without TTS credentials.
