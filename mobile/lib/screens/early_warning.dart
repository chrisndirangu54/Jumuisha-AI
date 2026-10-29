import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class EarlyWarningScreen extends StatefulWidget {
  final String baseUrl;
  final bool isSwahili;
  const EarlyWarningScreen({super.key, required this.baseUrl, this.isSwahili = false});

  @override
  State<EarlyWarningScreen> createState() => _EarlyWarningScreenState();
}

class _EarlyWarningScreenState extends State<EarlyWarningScreen> {
  late Future<List<dynamic>> future;
  final county = TextEditingController();
  bool showExercises = false;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  void refresh() {
    final query = <String, String>{
      if (county.text.trim().isNotEmpty) 'county': county.text.trim(),
      if (showExercises) 'include_exercises': 'true',
    };
    future = http.get(Uri.parse('${widget.baseUrl}/v1/early-warning/alerts').replace(queryParameters: query))
        .timeout(const Duration(seconds: 10))
        .then((r) {
          if (r.statusCode != 200) throw Exception('Alert service unavailable');
          return jsonDecode(r.body) as List<dynamic>;
        });
  }

  @override
  void dispose() {
    county.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final sw = widget.isSwahili;
    return Scaffold(
      appBar: AppBar(title: Text(sw ? 'Tahadhari za Umma' : 'Public Early Warnings')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        Card(child: Padding(
          padding: const EdgeInsets.all(12),
          child: Text(sw
              ? 'Mfumo wa majaribio pekee. Haufuatilii dharura za sasa. Fuata matangazo rasmi.'
              : 'Demonstration only. This system does not monitor live emergencies. Follow official authorities.',
              style: Theme.of(context).textTheme.bodyLarge),
        )),
        const SizedBox(height: 12),
        TextField(
          controller: county,
          decoration: InputDecoration(
            labelText: sw ? 'Kaunti (si lazima)' : 'County (optional)',
            border: const OutlineInputBorder(),
          ),
          onSubmitted: (_) => setState(refresh),
        ),
        SwitchListTile(
          title: Text(sw ? 'Onyesha mazoezi (si tahadhari halisi)' : 'Show training exercises (not real alerts)'),
          value: showExercises,
          onChanged: (v) => setState(() { showExercises = v; refresh(); }),
        ),
        FilledButton.icon(
          onPressed: () => setState(refresh),
          icon: const Icon(Icons.refresh),
          label: Text(sw ? 'Onyesha upya' : 'Refresh alerts'),
        ),
        const SizedBox(height: 14),
        FutureBuilder<List<dynamic>>(
          future: future,
          builder: (context, snapshot) {
            if (snapshot.hasError) return Text(sw ? 'Imeshindikana kupata taarifa. Jaribu tena.' : 'Could not load alerts. Try again.');
            if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
            final items = snapshot.data!;
            if (items.isEmpty) return Text(sw
              ? 'Hakuna tahadhari zilizothibitishwa kwenye mfumo huu. Hii haimaanishi kuwa hakuna hatari.'
              : 'No verified alerts available in this system. This does NOT mean conditions are safe.');
            return Column(children: [
              for (final raw in items)
                Builder(builder: (context) {
                  final a = raw as Map<String, dynamic>;
                  final exercise = a['status'] != 'actual';
                  return Card(child: Semantics(
                    label: exercise ? 'TRAINING EXERCISE' : 'Verified alert',
                    child: ListTile(
                      leading: Icon(exercise ? Icons.school_outlined : Icons.warning_amber_rounded),
                      title: Text((sw ? a['headline_sw'] : a['headline_en']) as String),
                      subtitle: Text('${exercise ? "EXERCISE / MAZOEZI — " : ""}${a['county'] ?? "National"} • ${a['severity']}\n${sw ? a['instruction_sw'] : a['instruction_en']}\nSource: ${a['source_name']}\nExpires: ${a['expires_at']}',
                      ),
                      isThreeLine: true,
                    ),
                  ));
                }),
            ]);
          },
        ),
      ]),
    );
  }
}
