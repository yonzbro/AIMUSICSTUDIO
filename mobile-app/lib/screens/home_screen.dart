import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _bgController;
  Map<String, dynamic> _serviceStatus = {};
  bool _gatewayOnline = false;
  bool _loadingStatus = true;

  @override
  void initState() {
    super.initState();
    _bgController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
    )..repeat(reverse: true);
    _checkServices();
  }

  Future<void> _checkServices() async {
    setState(() => _loadingStatus = true);
    final alive = await ApiService.checkHealth();
    Map<String, dynamic> status = {};
    if (alive) {
      status = await ApiService.getServicesStatus();
    }
    if (mounted) {
      setState(() {
        _gatewayOnline = alive;
        _serviceStatus = status;
        _loadingStatus = false;
      });
    }
  }

  @override
  void dispose() {
    _bgController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D1A),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Header ──────────────────────────────────────────
              Row(
                children: [
                  AnimatedBuilder(
                    animation: _bgController,
                    builder: (_, child) => Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: RadialGradient(
                          colors: [
                            Color.lerp(
                              const Color(0xFF7C3AED),
                              const Color(0xFF4F46E5),
                              _bgController.value,
                            )!,
                            const Color(0xFF1E1B4B),
                          ],
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF7C3AED)
                                .withValues(alpha: 0.4),
                            blurRadius: 20,
                          ),
                        ],
                      ),
                      child: const Icon(Icons.music_note,
                          color: Colors.white, size: 26),
                    ),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Antigravity',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 1,
                          ),
                        ),
                        Text(
                          'AI Music Studio',
                          style: TextStyle(
                            color: Colors.white38,
                            fontSize: 13,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Status indicator
                  _StatusDot(
                    online: _gatewayOnline,
                    loading: _loadingStatus,
                    onTap: _checkServices,
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // ── Hero Banner ─────────────────────────────────────
              AnimatedBuilder(
                animation: _bgController,
                builder: (_, child) => Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(24),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color.lerp(
                          const Color(0xFF7C3AED),
                          const Color(0xFF4F46E5),
                          _bgController.value,
                        )!,
                        const Color(0xFF1E1B4B),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color:
                            const Color(0xFF7C3AED).withValues(alpha: 0.3),
                        blurRadius: 30,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Create anything\nwith AI 🎶',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                          height: 1.2,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Generate lyrics, compose music, clone voices — all in one studio.',
                        style: TextStyle(
                          color: Colors.white60,
                          fontSize: 14,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 28),

              // ── Section Label ───────────────────────────────────
              const Text(
                'STUDIO',
                style: TextStyle(
                  color: Colors.white38,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 14),

              // ── Feature Cards ───────────────────────────────────
              _FeatureCard(
                icon: Icons.auto_awesome,
                title: 'Create Song',
                subtitle: 'Prompt → lyrics, music & voice',
                gradient: const [Color(0xFF7C3AED), Color(0xFF4F46E5)],
                statusWidgets: _buildServiceChips(['lyrics', 'music', 'voice']),
                onTap: () => Navigator.pushNamed(context, '/create'),
              ),
              const SizedBox(height: 14),
              _FeatureCard(
                icon: Icons.transform,
                title: 'Remix',
                subtitle: 'Upload a song → separate stems',
                gradient: const [Color(0xFFEC4899), Color(0xFFBE185D)],
                statusWidgets: _buildServiceChips(['remix']),
                onTap: () => Navigator.pushNamed(context, '/remix'),
              ),
              const SizedBox(height: 14),
              _FeatureCard(
                icon: Icons.mic,
                title: 'Voice Clone',
                subtitle: 'Upload voice sample → AI profile',
                gradient: const [Color(0xFF06B6D4), Color(0xFF0891B2)],
                statusWidgets: _buildServiceChips(['clone']),
                onTap: () => Navigator.pushNamed(context, '/voice_upload'),
              ),

              const SizedBox(height: 28),

              // ── Services Section ────────────────────────────────
              const Text(
                'SERVICES',
                style: TextStyle(
                  color: Colors.white38,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 14),

              // Service status cards
              ..._serviceStatus.entries.map((e) => _ServiceStatusTile(
                    name: e.key,
                    alive: e.value['alive'] ?? false,
                    modelLoaded: e.value['model_loaded'] ?? false,
                    modelName: e.value['model_name'] ?? '',
                    onLoadModel: () async {
                      final ok = await ApiService.loadModel(e.key);
                      if (ok) _checkServices();
                    },
                  )),

              if (_serviceStatus.isEmpty && !_loadingStatus)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A2E),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF3D2A6E)),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.cloud_off,
                          color: Colors.white30, size: 40),
                      const SizedBox(height: 10),
                      const Text(
                        'Backend offline',
                        style: TextStyle(color: Colors.white54, fontSize: 14),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Start docker-compose to connect',
                        style: TextStyle(
                            color: Colors.white30, fontSize: 12),
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildServiceChips(List<String> names) {
    return names.map((name) {
      final data = _serviceStatus[name];
      final alive = data?['alive'] ?? false;
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: alive
              ? Colors.greenAccent.withValues(alpha: 0.15)
              : Colors.white.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: alive ? Colors.greenAccent : Colors.white30,
              ),
            ),
            const SizedBox(width: 5),
            Text(
              name,
              style: TextStyle(
                color: alive ? Colors.greenAccent : Colors.white38,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }).toList();
  }
}

// ── Status Dot ────────────────────────────────────────────────────
class _StatusDot extends StatelessWidget {
  final bool online;
  final bool loading;
  final VoidCallback onTap;
  const _StatusDot(
      {required this.online, required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: online
              ? Colors.greenAccent.withValues(alpha: 0.12)
              : Colors.redAccent.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: online
                ? Colors.greenAccent.withValues(alpha: 0.3)
                : Colors.redAccent.withValues(alpha: 0.3),
          ),
        ),
        child: loading
            ? const SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white54),
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: online ? Colors.greenAccent : Colors.redAccent,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    online ? 'Online' : 'Offline',
                    style: TextStyle(
                      color: online ? Colors.greenAccent : Colors.redAccent,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

// ── Feature Card ──────────────────────────────────────────────────
class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final List<Color> gradient;
  final List<Widget> statusWidgets;
  final VoidCallback onTap;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.gradient,
    required this.statusWidgets,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A2E),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFF2D2D4E)),
          boxShadow: [
            BoxShadow(
              color: gradient[0].withValues(alpha: 0.08),
              blurRadius: 20,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(14),
                gradient: LinearGradient(colors: gradient),
              ),
              child: Icon(icon, color: Colors.white, size: 26),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      color: Colors.white38,
                      fontSize: 12,
                    ),
                  ),
                  if (statusWidgets.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Wrap(spacing: 6, children: statusWidgets),
                  ],
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.white24, size: 24),
          ],
        ),
      ),
    );
  }
}

// ── Service Status Tile ───────────────────────────────────────────
class _ServiceStatusTile extends StatefulWidget {
  final String name;
  final bool alive;
  final bool modelLoaded;
  final String modelName;
  final Future<void> Function() onLoadModel;

  const _ServiceStatusTile({
    required this.name,
    required this.alive,
    required this.modelLoaded,
    required this.modelName,
    required this.onLoadModel,
  });

  @override
  State<_ServiceStatusTile> createState() => _ServiceStatusTileState();
}

class _ServiceStatusTileState extends State<_ServiceStatusTile> {
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: widget.alive
              ? const Color(0xFF2D2D4E)
              : Colors.redAccent.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: !widget.alive
                  ? Colors.redAccent
                  : widget.modelLoaded
                      ? Colors.greenAccent
                      : Colors.amber,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.name.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                  ),
                ),
                if (widget.modelName.isNotEmpty)
                  Text(
                    widget.modelName,
                    style: const TextStyle(color: Colors.white30, fontSize: 11),
                  ),
              ],
            ),
          ),
          if (widget.alive && !widget.modelLoaded)
            _loading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.amber),
                  )
                : GestureDetector(
                    onTap: () async {
                      setState(() => _loading = true);
                      await widget.onLoadModel();
                      if (mounted) setState(() => _loading = false);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: Colors.amber.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'Load Model',
                        style: TextStyle(
                          color: Colors.amber,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
          if (widget.alive && widget.modelLoaded)
            const Icon(Icons.check_circle, color: Colors.greenAccent, size: 20),
          if (!widget.alive)
            const Icon(Icons.error_outline, color: Colors.redAccent, size: 20),
        ],
      ),
    );
  }
}
