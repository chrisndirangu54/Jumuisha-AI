import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import '../main.dart';

/// Local-only notes: does not collect identity numbers or health information.
/// Users can review/delete drafts. This is not an official submission.
class PublicServiceJourney extends StatefulWidget {
  final GovernmentService service;
  const PublicServiceJourney({super.key, required this.service});
  @override
  State<PublicServiceJourney> createState() => _PublicServiceJourneyState();
}

class _PublicServiceJourneyState extends State<PublicServiceJourney> {
  final note = TextEditingController();
  bool consent = false;
  bool loading = true;
  String? status;
  List<String> steps = [];
  @override
  void initState() {
    super.initState();
    _load();
  }
  String get draftKey => 'service_draft_${widget.service.id}';
  Future<void> _load() async {
    final store = await SharedPreferences.getInstance();
    final saved = store.getString(draftKey);
    if (saved != null) note.text = saved;
    try {
      final response = await http.get(Uri.parse('$baseUrl/v1/services/${widget.service.id}/guide'))
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        steps = (data['steps'] as List<dynamic>)
            .map((e) => (e as Map<String, dynamic>)['label'] as String).toList();
      }
    } catch (_) {
      // Public guidance from catalogue remains available without connectivity.
    }
    if (mounted) setState(() => loading = false);
  }
  Future<void> _save() async {
    if (!consent) return;
    final store = await SharedPreferences.getInstance();
    await store.setString(draftKey, note.text);
    if (mounted) setState(() => status='Saved on this device only. Not sent to government.');
  }
  Future<void> _delete() async {
    final store = await SharedPreferences.getInstance();
    await store.remove(draftKey);
    note.clear();
    if (mounted) setState(() => status='Local note deleted.');
  }
  @override
  void dispose() { note.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.service.name)),
    body: ListView(padding: const EdgeInsets.all(20), children: [
      Text(widget.service.description, style: Theme.of(context).textTheme.bodyLarge),
      const SizedBox(height: 14),
      const Text('This guide is not a government application. Check official requirements and fees.'),
      const SizedBox(height: 16),
      Text('How to continue', style: Theme.of(context).textTheme.titleLarge),
      if (loading) const LinearProgressIndicator(),
      if (steps.isEmpty && !loading)
        const Text('Review agency requirements, prepare approved documents, and continue at the official portal.'),
      for (var i=0;i<steps.length;i++)
        ListTile(leading: CircleAvatar(child: Text('${i+1}')), title: Text(steps[i])),
      const SizedBox(height: 16),
      SelectableText('Official government website: ${widget.service.officialUrl}'),
      const SizedBox(height: 14),
      Text('Private planning note (optional)', style: Theme.of(context).textTheme.titleMedium),
      const Text('Do not enter ID numbers, passwords, medical records or payment details. Local notes are not encrypted.'),
      TextField(
        controller: note,
        maxLength: 1000,
        maxLines: 3,
        decoration: const InputDecoration(
          border: OutlineInputBorder(), hintText: 'Example: ask for accessible appointment assistance'),
      ),
      CheckboxListTile(
        value: consent,
        title: const Text('I agree to save this non-sensitive note on my device'),
        onChanged: (v) => setState(() => consent=v ?? false),
      ),
      FilledButton.icon(
        onPressed: consent ? _save : null,
        icon: const Icon(Icons.save_alt),
        label: const Text('Save local note'),
      ),
      TextButton.icon(
        onPressed: _delete,
        icon: const Icon(Icons.delete_outline),
        label: const Text('Delete local note'),
      ),
      if (status != null) Semantics(liveRegion: true, child: Text(status!)),
      const Divider(),
      const Text('For KSL, request a qualified interpreter or use reviewed signing media when available.'),
    ]),
  );
}
