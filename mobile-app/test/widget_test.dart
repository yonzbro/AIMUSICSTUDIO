// This is a basic Flutter widget test.

import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Smoke test for AntigravityMusicApp', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const AntigravityMusicApp());

    // Verify that the title or base widgets exist.
    expect(find.text('Create Music'), findsOneWidget);
  });
}
