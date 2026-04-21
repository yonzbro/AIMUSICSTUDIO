import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import '../services/api_service.dart';

class VoiceUploadScreen extends StatefulWidget {
  const VoiceUploadScreen({super.key});

  @override
  State<VoiceUploadScreen> createState() => _VoiceUploadScreenState();
}

class _VoiceUploadScreenState extends State<VoiceUploadScreen>
    with SingleTickerProviderStateMixin {
  bool _isUploading = false;
  String? _profileId;
  String? _selectedFileName;
  String _statusMessage = 'Upload a short voice sample (10–30 sec WAV/MP3)';

  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _glowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _glowAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _glowController.dispose();
    super.dispose();
  }

  Future<void> _pickAndUpload() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3', 'm4a', 'aac'],
      allowMultiple: false,
    );

    if (result == null || result.files.isEmpty) return;

    final file = result.files.first;
    if (file.path == null) {
      setState(() => _statusMessage = 'Could not access file path.');
      return;
    }

    setState(() {
      _selectedFileName = file.name;
      _statusMessage = 'File selected: ${file.name}';
    });

    await _uploadFile(file.path!);
  }

  Future<void> _uploadFile(String filePath) async {
    setState(() {
      _isUploading = true;
      _statusMessage = 'Uploading and processing voice sample…';
    });

    try {
      final uri = Uri.parse('${ApiService.baseUrl}/services/clone/clone-voice');
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 60),
      );
      final body = await streamedResponse.stream.bytesToString();

      if (streamedResponse.statusCode == 200) {
        final data = jsonDecode(body);
        setState(() {
          _profileId = data['voice_profile_id'] ?? 'unknown';
          _statusMessage = '✅ Voice profile created!\nID: $_profileId';
        });
      } else {
        setState(() => _statusMessage =
            '❌ Upload failed (${streamedResponse.statusCode}). Try again.');
      }
    } catch (e) {
      setState(() => _statusMessage = '❌ Connection error: $e');
    } finally {
      setState(() => _isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white70),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Clone Your Voice',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Header info ───────────────────────────────────────
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A2E),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF3D2A6E)),
              ),
              child: const Column(
                children: [
                  Icon(Icons.info_outline, color: Colors.deepPurpleAccent),
                  SizedBox(height: 8),
                  Text(
                    'Record or upload a clear voice sample for AI voice cloning. '
                    'Speak naturally for 10–30 seconds without background noise.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: Colors.white60, fontSize: 13, height: 1.5),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // ── Mic animation ─────────────────────────────────────
            Center(
              child: AnimatedBuilder(
                animation: _glowAnimation,
                builder: (context, child) {
                  return Container(
                    width: 160,
                    height: 160,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF1A1A2E),
                      border: Border.all(
                        color: _profileId != null
                            ? Colors.greenAccent
                                .withValues(alpha: _glowAnimation.value)
                            : const Color(0xFF06B6D4)
                                .withValues(alpha: _glowAnimation.value),
                        width: 3,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: _profileId != null
                              ? Colors.greenAccent
                                  .withValues(alpha: _glowAnimation.value * 0.3)
                              : const Color(0xFF06B6D4)
                                  .withValues(alpha: _glowAnimation.value * 0.4),
                          blurRadius: 40,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Icon(
                      _profileId != null ? Icons.check_circle : Icons.mic,
                      size: 72,
                      color: _profileId != null
                          ? Colors.greenAccent
                          : const Color(0xFF06B6D4),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 20),

            // ── Selected file name ────────────────────────────────
            if (_selectedFileName != null)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A2E),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF3D2A6E)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.audio_file,
                        color: Color(0xFF06B6D4), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _selectedFileName!,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 16),

            // ── Status message ────────────────────────────────────
            Text(
              _statusMessage,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _profileId != null ? Colors.greenAccent : Colors.white60,
                fontSize: 13,
                height: 1.5,
              ),
            ),

            const Spacer(),

            // ── Buttons ───────────────────────────────────────────
            if (!_isUploading) ...[
              _buildButton(
                icon: Icons.upload_file,
                label: 'Pick & Upload Voice Sample',
                onTap: _pickAndUpload,
                gradient: const LinearGradient(
                  colors: [Color(0xFF06B6D4), Color(0xFF0891B2)],
                ),
              ),
              const SizedBox(height: 14),
              _buildButton(
                icon: Icons.mic,
                label: 'Record In-App (Coming Soon)',
                onTap: null,
                gradient: const LinearGradient(
                  colors: [Color(0xFF2D2D4E), Color(0xFF2D2D4E)],
                ),
              ),
            ] else
              const Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(color: Color(0xFF06B6D4)),
                    SizedBox(height: 16),
                    Text('Processing voice sample…',
                        style: TextStyle(color: Colors.white60)),
                  ],
                ),
              ),

            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildButton({
    required IconData icon,
    required String label,
    required VoidCallback? onTap,
    required LinearGradient gradient,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 54,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          gradient: gradient,
          boxShadow: onTap != null
              ? [
                  BoxShadow(
                    color: const Color(0xFF06B6D4).withValues(alpha: 0.35),
                    blurRadius: 16,
                    offset: const Offset(0, 5),
                  ),
                ]
              : [],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon,
                color: onTap != null ? Colors.white : Colors.white38,
                size: 20),
            const SizedBox(width: 10),
            Text(
              label,
              style: TextStyle(
                color: onTap != null ? Colors.white : Colors.white38,
                fontWeight: FontWeight.bold,
                fontSize: 15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
