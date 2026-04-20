import 'package:flutter/material.dart';
import 'screens/music_prompt_screen.dart';
import 'screens/player_screen.dart';
import 'screens/voice_upload_screen.dart';

void main() {
  runApp(const AntigravityMusicApp());
}

class AntigravityMusicApp extends StatelessWidget {
  const AntigravityMusicApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Antigravity AI Music Studio',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF7C3AED),
          secondary: const Color(0xFF4F46E5),
          surface: const Color(0xFF1A1A2E),
          background: const Color(0xFF0D0D1A),
        ),
        scaffoldBackgroundColor: const Color(0xFF0D0D1A),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0D0D1A),
          elevation: 0,
        ),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const MusicPromptScreen(),
        '/player': (context) => const PlayerScreen(),
        '/voice_upload': (context) => const VoiceUploadScreen(),
      },
    );
  }
}
