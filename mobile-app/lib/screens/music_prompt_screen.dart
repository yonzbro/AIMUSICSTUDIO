import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class MusicPromptScreen extends StatefulWidget {
  const MusicPromptScreen({super.key});

  @override
  State<MusicPromptScreen> createState() => _MusicPromptScreenState();
}

class _MusicPromptScreenState extends State<MusicPromptScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _promptController = TextEditingController();
  String _selectedStyle = 'Deep House';
  final List<String> _styles = [
    'Deep House',
    'House',
    'Trap',
    'Chill',
    'Electronic',
    'Lo-Fi',
    'Ambient',
    'Hip-Hop',
    'Pop',
    'R&B',
    'Jazz',
    'Classical',
  ];

  // ── Feature toggles ────────────────────────────────────────────
  final Map<String, bool> _features = {
    'lyrics': true,
    'music': true,
    'voice': true,
  };

  final Map<String, IconData> _featureIcons = {
    'lyrics': Icons.text_snippet,
    'music': Icons.piano,
    'voice': Icons.record_voice_over,
  };

  final Map<String, String> _featureLabels = {
    'lyrics': 'Lyrics',
    'music': 'Music',
    'voice': 'Voice',
  };

  bool _isLoading = false;
  String _loadingStep = '';

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  // ── Voice profiles ────────────────────────────────────────────
  List<dynamic> _voiceProfiles = [];
  String? _selectedVoiceId;
  bool _useRvc = true;
  double _rvcPitch = 0.0;
  double _rvcIndexRate = 0.75;

  @override
  void initState() {
    super.initState();
    _fetchProfiles();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  Future<void> _fetchProfiles() async {
    final data = await ApiService.getServicesStatus();
    if (data.containsKey('clone')) {
       // We'll get profiles from the dedicated endpoint we added
       try {
         final resp = await http.get(Uri.parse('${ApiService.baseUrl}/voice-profiles'));
         if (resp.statusCode == 200) {
           final body = jsonDecode(resp.body);
           setState(() {
             _voiceProfiles = body['profiles'] ?? [];
             if (_voiceProfiles.isNotEmpty) {
               _selectedVoiceId = _voiceProfiles.first['profile_id'];
             }
           });
         }
       } catch(_) {}
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _promptController.dispose();
    super.dispose();
  }

  List<String> get _activeFeatures =>
      _features.entries.where((e) => e.value).map((e) => e.key).toList();

  Future<void> _generateSong() async {
    if (_promptController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Describe your song first!'),
          backgroundColor: Colors.red.shade700,
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      return;
    }

    if (_activeFeatures.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Enable at least one feature!'),
          backgroundColor: Colors.amber.shade700,
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _loadingStep = 'Sending to AI pipeline…';
    });

    try {
      final data = await ApiService.generateSong(
        prompt: _promptController.text,
        style: _selectedStyle,
        features: _activeFeatures,
        voiceProfileId: _selectedVoiceId,
        useRvc: _useRvc,
        rvcPitch: _rvcPitch.toInt(),
        rvcIndexRate: _rvcIndexRate,
      );

      if (data != null && mounted) {
        Navigator.pushNamed(context, '/player', arguments: {
          'prompt': _promptController.text,
          'style': _selectedStyle,
          'final_song': data['final_song'],
          'lyrics': data['lyrics'] ?? '',
          'features_used': data['features_used'] ?? [],
        });
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Generation failed. Check backend logs.'),
            backgroundColor: Colors.red.shade700,
            behavior: SnackBarBehavior.floating,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red.shade700,
            behavior: SnackBarBehavior.floating,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
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
          'Create Song',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            letterSpacing: 0.5,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Animated Icon ─────────────────────────────────────
            Center(
              child: ScaleTransition(
                scale: _pulseAnimation,
                child: Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const RadialGradient(
                      colors: [Color(0xFF7C3AED), Color(0xFF1E1B4B)],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF7C3AED).withValues(alpha: 0.5),
                        blurRadius: 30,
                        spreadRadius: 3,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.auto_awesome,
                    size: 40,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // ── Title ─────────────────────────────────────────────
            const Text(
              'Describe your song',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'Toggle the AI features you want below',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Colors.white38),
            ),
            const SizedBox(height: 24),

            // ── Feature Toggles ───────────────────────────────────
            Row(
              children: _features.keys.map((key) {
                final on = _features[key]!;
                return Expanded(
                  child: GestureDetector(
                    onTap: () =>
                        setState(() => _features[key] = !_features[key]!),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 250),
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      decoration: BoxDecoration(
                        color: on
                            ? const Color(0xFF7C3AED).withValues(alpha: 0.18)
                            : const Color(0xFF1A1A2E),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: on
                              ? const Color(0xFF7C3AED)
                              : const Color(0xFF2D2D4E),
                          width: on ? 2 : 1,
                        ),
                      ),
                      child: Column(
                        children: [
                          Icon(
                            _featureIcons[key],
                            color: on ? const Color(0xFF7C3AED) : Colors.white30,
                            size: 24,
                          ),
                          const SizedBox(height: 6),
                          Text(
                            _featureLabels[key]!,
                            style: TextStyle(
                              color: on ? Colors.white : Colors.white30,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Container(
                            width: 18,
                            height: 18,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: on
                                  ? const Color(0xFF7C3AED)
                                  : Colors.transparent,
                              border: Border.all(
                                color: on
                                    ? const Color(0xFF7C3AED)
                                    : Colors.white24,
                                width: 2,
                              ),
                            ),
                            child: on
                                ? const Icon(Icons.check,
                                    size: 12, color: Colors.white)
                                : null,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // ── Prompt field ──────────────────────────────────────
            TextField(
              controller: _promptController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'e.g. a dreamy lo-fi beat about late night coding…',
                hintStyle: const TextStyle(color: Colors.white24),
                filled: true,
                fillColor: const Color(0xFF1A1A2E),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: const BorderSide(color: Color(0xFF3D2A6E)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: const BorderSide(color: Color(0xFF3D2A6E)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide:
                      const BorderSide(color: Color(0xFF7C3AED), width: 2),
                ),
              ),
            ),
            const SizedBox(height: 18),

            // ── Style chips ───────────────────────────────────────
            const Text(
              'STYLE',
              style: TextStyle(
                color: Colors.white38,
                fontSize: 11,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _styles.map((style) {
                final sel = style == _selectedStyle;
                return GestureDetector(
                  onTap: () => setState(() => _selectedStyle = style),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: sel
                          ? const Color(0xFF7C3AED)
                          : const Color(0xFF1A1A2E),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: sel
                            ? const Color(0xFF7C3AED)
                            : const Color(0xFF2D2D4E),
                      ),
                    ),
                    child: Text(
                      style,
                      style: TextStyle(
                        color: sel ? Colors.white : Colors.white54,
                        fontSize: 13,
                        fontWeight: sel ? FontWeight.w700 : FontWeight.w500,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 32),

            // ── Voice & RVC Settings ──────────────────────────────
            if (_features['voice']!) ...[
              const Text(
                'VOICE SETTINGS',
                style: TextStyle(
                  color: Colors.white38,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.5,
                ),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A2E),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF2D2D4E)),
                ),
                child: Column(
                  children: [
                    // Voice Profile Dropdown
                    DropdownButtonFormField<String>(
                      value: _selectedVoiceId,
                      dropdownColor: const Color(0xFF1A1A2E),
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: 'Select Voice',
                        labelStyle: TextStyle(color: Colors.white30),
                        enabledBorder: InputBorder.none,
                      ),
                      items: [
                        const DropdownMenuItem(
                            value: null, child: Text('Default AI Voice')),
                        ..._voiceProfiles.map((p) => DropdownMenuItem(
                              value: p['profile_id'] as String,
                              child: Text(p['profile_id'] as String),
                            )),
                      ],
                      onChanged: (val) => setState(() => _selectedVoiceId = val),
                    ),
                    const Divider(color: Colors.white10),
                    // RVC Toggle
                    SwitchListTile(
                      title: const Text('High-Fidelity RVC',
                          style: TextStyle(color: Colors.white, fontSize: 14)),
                      subtitle: const Text('Uses neural conversion for maximum realism',
                          style: TextStyle(color: Colors.white30, fontSize: 11)),
                      value: _useRvc,
                      activeColor: const Color(0xFF7C3AED),
                      onChanged: (val) => setState(() => _useRvc = val),
                    ),
                    if (_useRvc) ...[
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          const Text('Pitch',
                              style: TextStyle(color: Colors.white70, fontSize: 12)),
                          Expanded(
                            child: Slider(
                              value: _rvcPitch,
                              min: -12,
                              max: 12,
                              divisions: 24,
                              label: _rvcPitch.toInt().toString(),
                              activeColor: const Color(0xFF7C3AED),
                              onChanged: (val) => setState(() => _rvcPitch = val),
                            ),
                          ),
                          Text('${_rvcPitch.toInt()}',
                              style: const TextStyle(color: Colors.white)),
                        ],
                      ),
                      Row(
                        children: [
                          const Text('Strength',
                              style: TextStyle(color: Colors.white70, fontSize: 12)),
                          Expanded(
                            child: Slider(
                              value: _rvcIndexRate,
                              min: 0.0,
                              max: 1.0,
                              divisions: 10,
                              label: _rvcIndexRate.toStringAsFixed(1),
                              activeColor: const Color(0xFF7C3AED),
                              onChanged: (val) =>
                                  setState(() => _rvcIndexRate = val),
                            ),
                          ),
                          Text(_rvcIndexRate.toStringAsFixed(1),
                              style: const TextStyle(color: Colors.white)),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 24),
            ],

            // ── Generate button ───────────────────────────────────
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              height: 58,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: _isLoading
                    ? const LinearGradient(
                        colors: [Color(0xFF3D2A6E), Color(0xFF3D2A6E)],
                      )
                    : const LinearGradient(
                        colors: [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                boxShadow: _isLoading
                    ? []
                    : [
                        BoxShadow(
                          color:
                              const Color(0xFF7C3AED).withValues(alpha: 0.45),
                          blurRadius: 20,
                          offset: const Offset(0, 6),
                        ),
                      ],
              ),
              child: ElevatedButton(
                onPressed: _isLoading ? null : _generateSong,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: _isLoading
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            _loadingStep,
                            style: const TextStyle(
                                fontSize: 14, color: Colors.white70),
                          ),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.auto_awesome,
                              color: Colors.white, size: 20),
                          const SizedBox(width: 10),
                          Text(
                            'Generate (${_activeFeatures.length} feature${_activeFeatures.length == 1 ? "" : "s"})',
                            style: const TextStyle(
                              fontSize: 16,
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
