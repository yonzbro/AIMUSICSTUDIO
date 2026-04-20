import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class VoiceUploadScreen extends StatefulWidget {
  const VoiceUploadScreen({super.key});

  @override
  State<VoiceUploadScreen> createState() => _VoiceUploadScreenState();
}

class _VoiceUploadScreenState extends State<VoiceUploadScreen>
    with SingleTickerProviderStateMixin {
  bool _isUploading = false;
  String? _profileId;
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
    // NOTE: file_picker integration — add `file_picker` to pubspec.yaml to enable.
    // For now, show a coming-soon snackbar.
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
            'Voice cloning coming soon! Add file_picker package to enable.'),
        backgroundColor: Color(0xFF7C3AED),
        duration: Duration(seconds: 3),
      ),
    );
  }

  Future<void> _uploadFile(String filePath) async {
    setState(() {
      _isUploading = true;
      _statusMessage = 'Uploading and processing voice sample…';
    });

    try {
      final uri = Uri.parse('http://10.0.2.2:8004/clone-voice');
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final response = await request.send();
      final body = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        // Parse profileId from response
        setState(() {
          _profileId = 'voice_profile_saved';
          _statusMessage = '✅ Voice profile created successfully!';
        });
      } else {
        setState(() => _statusMessage = 'Upload failed. Try again.');
      }
    } catch (e) {
      setState(() => _statusMessage = 'Error: $e');
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
                    style: TextStyle(color: Colors.white60, fontSize: 13, height: 1.5),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 40),

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
                        color: const Color(0xFF7C3AED)
                            .withOpacity(_glowAnimation.value),
                        width: 3,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF7C3AED)
                              .withOpacity(_glowAnimation.value * 0.4),
                          blurRadius: 40,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.mic,
                      size: 72,
                      color: Color(0xFF7C3AED),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 24),

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

            // ── Upload button ─────────────────────────────────────
            if (!_isUploading) ...[
              _buildButton(
                icon: Icons.upload_file,
                label: 'Upload Voice Sample',
                onTap: _pickAndUpload,
                gradient: const LinearGradient(
                  colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
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
                    CircularProgressIndicator(color: Color(0xFF7C3AED)),
                    SizedBox(height: 16),
                    Text('Processing…',
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
                    color: const Color(0xFF7C3AED).withOpacity(0.35),
                    blurRadius: 16,
                    offset: const Offset(0, 5),
                  ),
                ]
              : [],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: onTap != null ? Colors.white : Colors.white38, size: 20),
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
