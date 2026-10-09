import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jumuisha_ai/screens/voice_search.dart';

void main() {
  testWidgets('voice search has keyboard alternative and clear privacy notice', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: VoiceServiceSearch()));
    expect(find.byType(TextField), findsOneWidget);
    expect(find.textContaining('Avoid speaking sensitive information'), findsOneWidget);
    expect(find.text('Speak service name'), findsOneWidget);
    expect(find.text('Use this search'), findsOneWidget);
  });
}
