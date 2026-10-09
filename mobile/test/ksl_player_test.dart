import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jumuisha_ai/screens/ksl_player.dart';

void main() {
  testWidgets('unapproved KSL media never plays and has accessible fallback', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(
      body: KslPlayer(approvedAsset: null, reviewed: false, caption: 'Please visit the official office'),
    )));
    await tester.pump();
    expect(find.textContaining('No human-reviewed KSL recording'), findsOneWidget);
    expect(find.text('Please visit the official office'), findsOneWidget);
  });
}
