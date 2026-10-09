import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jumuisha_ai/main.dart';

void main() {
  testWidgets('shows accessibility controls', (tester) async {
    await tester.pumpWidget(const JumuishaApp());
    expect(find.text('Jumuisha AI'), findsOneWidget);
    expect(find.text('High contrast'), findsOneWidget);
    expect(find.text('Reduce motion'), findsOneWidget);
    expect(find.byType(Slider), findsOneWidget);
  });
}
