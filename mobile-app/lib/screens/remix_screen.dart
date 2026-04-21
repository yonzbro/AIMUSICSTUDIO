import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:audioplayers/audioplayers.dart';
import '../services/api_service.dart';

class RemixScreen extends StatefulWidget {
  const RemixScreen({super.key});

  @override
  State<RemixScreen> createState() => _RemixScreenState();
}

class _RemixScreenState extends State<RemixScreen>
    with SingleTickerProviderStateMixin {
  bool _isProcessing = false;
  String? _selectedFile;
  List<String> _stems = [];
  String _status = 'Upload a song to separate its stems';

  final Map<String, AudioPlayer> _players = {};
  final Map<String, bool> _playing = {};

  late AnimationController _waveController;

  // Stem metadata
  static const Map<String, _StemInfo> _stemMeta = {
    'vocals': _StemInfo(Icons.mic, Color(0xFFEC4899), 'Vocals'),
    'drums': _StemInfo(Icons.music_note, Color(0xFFF59E0B), 'Drums'),
    'bass': _StemInfo(Icons.graphic_eq, Color(0xFF06B6D4), 'Bass'),
    'other': _StemInfo(Icons.piano, Color(0xFF8B5CF6), 'Other'),
  };

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _waveController.dispose();
    for (final p in _players.values) {
      p.dispose();
    }
    super.dispose();
  }

  Future<void> _pickAndRemix() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3', 'm4a', 'aac', 'flac'],
      allowMultiple: false,
    );

    if (result == null || result.files.isEmpty || result.files.first.path == null) return;

    final file = result.files.first;

    setState(() {
      _selectedFile = file.name;
      _isProcessing = true;
      _status = 'Separating stems with Demucs AI…';
      _stems = [];
    });

    final resp = await ApiService.remixAudio(file.path!);

    if (resp != null && resp['stems'] != null) {
      setState(() {
        _stems = List<String>.from(resp['stems']);
        _status = '✅ ${_stems.length} stems separated!';
        _isProcessing = false;
      });
    } else {
      setState(() {
        _status = '❌ Remix failed. Is the remix service running?';
        _isProcessing = false;
      });
    }
  }

  Future<void> _toggleStem(String stem) async {
    if (!_players.containsKey(stem)) {
      _players[stem] = AudioPlayer();
      _playing[stem] = false;
    }

    final player = _players[stem]!;
    final isPlaying = _playing[stem] ?? false;

    if (isPlaying) {
      await player.pause();
      setState(() => _playing[stem] = false);
    } else {
      final url = ApiService.audioUrl(stem);
      await player.play(UrlSource(url));
      setState(() => _playing[stem] = true);

      player.onPlayerStateChanged.listen((state) {
        if (mounted && state != PlayerState.playing) {
          setState(() => _playing[stem] = false);
        }
      });
    }
  }

  String _stemType(String filename) {
    final lower = filename.toLowerCase();
    for (final key in _stemMeta.keys) {
      if (lower.contains(key)) return key;
    }
    return 'other';
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
          'Remix',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Waveform animation ────────────────────────────────
            Center(
              child: AnimatedBuilder(
                animation: _waveController,
                builder: (_, child) => Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        const Color(0xFFEC4899)
                            .withValues(alpha: 0.3 + _waveController.value * 0.4),
                        const Color(0xFF1E1B4B),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFEC4899)
                            .withValues(alpha: 0.3),
                        blurRadius: 30,
                      ),
                    ],
                  ),
                  child: const Icon(Icons.transform,
                      color: Colors.white, size: 44),
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text(
              'Stem Separation',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            const Text(
              'Split any song into vocals, drums, bass & more',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white38, fontSize: 13),
            ),
            const SizedBox(height: 24),

            // ── Selected file ─────────────────────────────────────
            if (_selectedFile != null)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A2E),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF3D2A6E)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.audio_file,
                        color: Color(0xFFEC4899), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _selectedFile!,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 12),

            // ── Status ────────────────────────────────────────────
            Text(
              _status,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: _stems.isNotEmpty ? Colors.greenAccent : Colors.white54,
                fontSize: 13,
              ),
            ),

            const SizedBox(height: 20),

            // ── Stems list ────────────────────────────────────────
            if (_stems.isNotEmpty)
              Expanded(
                child: ListView.separated(
                  itemCount: _stems.length,
                  separatorBuilder: (_, index) => const SizedBox(height: 10),
                  itemBuilder: (_, i) {
                    final stem = _stems[i];
                    final type = _stemType(stem);
                    final meta =
                        _stemMeta[type] ?? _stemMeta['other']!;
                    final isPlaying = _playing[stem] ?? false;

                    return GestureDetector(
                      onTap: () => _toggleStem(stem),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 250),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: isPlaying
                              ? meta.color.withValues(alpha: 0.12)
                              : const Color(0xFF1A1A2E),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: isPlaying
                                ? meta.color
                                : const Color(0xFF2D2D4E),
                            width: isPlaying ? 2 : 1,
                          ),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(12),
                                color: meta.color.withValues(alpha: 0.2),
                              ),
                              child: Icon(meta.icon,
                                  color: meta.color, size: 22),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    meta.label,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 15,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  Text(
                                    stem,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                        color: Colors.white30, fontSize: 11),
                                  ),
                                ],
                              ),
                            ),
                            Icon(
                              isPlaying ? Icons.pause_circle : Icons.play_circle,
                              color: meta.color,
                              size: 36,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),

            if (_stems.isEmpty) const Spacer(),

            // ── Upload button ─────────────────────────────────────
            if (!_isProcessing)
              GestureDetector(
                onTap: _pickAndRemix,
                child: Container(
                  height: 56,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: const LinearGradient(
                      colors: [Color(0xFFEC4899), Color(0xFFBE185D)],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFEC4899).withValues(alpha: 0.35),
                        blurRadius: 16,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.upload_file, color: Colors.white, size: 20),
                      SizedBox(width: 10),
                      Text(
                        'Upload Song to Remix',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            if (_isProcessing)
              const Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(color: Color(0xFFEC4899)),
                    SizedBox(height: 14),
                    Text(
                      'AI is processing your song…',
                      style: TextStyle(color: Colors.white54),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _StemInfo {
  final IconData icon;
  final Color color;
  final String label;
  const _StemInfo(this.icon, this.color, this.label);
}
