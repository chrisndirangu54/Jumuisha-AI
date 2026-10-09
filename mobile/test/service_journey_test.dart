import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jumuisha_ai/main.dart';
import 'package:jumuisha_ai/screens/service_journey.dart';

void main() {
  testWidgets('service journey labels government submissions unavailable', (tester) async {
    final item = GovernmentService.fromJson({
      'id':'ecitizen',
      'name':'eCitizen services',
      'agency':'Government of Kenya',
      'description':'Information only',
      'official_url':'https://www.ecitizen.go.ke/',
      'status':'approval_required',
    });
    await tester.pumpWidget(MaterialApp(home: PublicServiceJourney(service:item)));
    await tester.pump();
    expect(find.textContaining('not a government application'), findsOneWidget);
    expect(find.text('Save local note'), findsOneWidget);
    expect(find.text('Delete local note'), findsOneWidget);
    final save = tester.widget<FilledButton>(find.widgetWithText(FilledButton,'Save local note'));
    expect(save.onPressed, isNull);
  });
}
