import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// Read-only warnings. No geolocation, subscriptions or emergency dispatch.
class EarlyWarningScreen extends StatefulWidget {
  final String apiBaseUrl;
  const EarlyWarningScreen({super.key, required this.apiBaseUrl});
  @override
  State<EarlyWarningScreen> createState() => _EarlyWarningScreenState();
}

class _EarlyWarningScreenState extends State<EarlyWarningScreen> {
  final countyController = TextEditingController();
  Future<List<dynamic>>? current;
  @override
  void initState() { super.initState(); refresh(); }
  void refresh() {
    final county = countyController.text.trim();
    final uri = Uri.parse('${widget.apiBaseUrl}/v1/early-warning/alerts')
      .replace(queryParameters: county.isEmpty ? null : {'county': county});
    setState(() => current = http.get(uri).timeout(const Duration(seconds: 10)).then((r) {
      if (r.statusCode != 200) throw Exception('Warnings cannot be verified now');
      return jsonDecode(r.body) as List<dynamic>;
    }));
  }
  @override
  void dispose() { countyController.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Public early warnings')),
    body: ListView(padding: const EdgeInsets.all(16), children: [
      const Text('Official warnings only. This pilot is not a guaranteed emergency notification service. For immediate danger, follow local emergency authority instructions.'),
      const SizedBox(height: 12),
      TextField(controller: countyController,
        decoration: const InputDecoration(labelText: 'County (optional)', hintText: 'e.g. Nairobi', border: OutlineInputBorder())),
      const SizedBox(height: 8),
      FilledButton.icon(onPressed: refresh, icon: const Icon(Icons.refresh), label: const Text('Check warnings')),
      const SizedBox(height: 12),
      FutureBuilder<List<dynamic>>(future: current, builder: (context, snap) {
        if (snap.hasError) return const Text('Unable to verify alerts. Check official local alerts directly.');
        if (!snap.hasData) return const Center(child: CircularProgressIndicator());
        if (snap.data!.isEmpty) return const Text('No verified active warnings are available from this pilot feed. This does NOT mean there is no danger.');
        return Column(children: [
          for (final raw in snap.data!)
            Card(child: Padding(padding: const EdgeInsets.all(12), child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(raw['title']?.toString() ?? 'Warning', style: Theme.of(context).textTheme.titleLarge),
                Text('${raw['severity']} · ${raw['hazard']} · ${raw['county']}'),
                const SizedBox(height: 6),
                Text(raw['description']?.toString() ?? ''),
                const SizedBox(height: 6),
                for (final step in (raw['instructions'] as List<dynamic>? ?? []))
                  Text('• $step'),
                Text('Source: ${raw['source_name']}'),
                Text('Valid until: ${raw['expires_at']}'),
              ]))),
        ]);
      }),
    ]),
  );
}
