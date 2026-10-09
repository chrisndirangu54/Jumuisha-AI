import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'services/assistive.dart';
import 'screens/service_journey.dart';
import 'screens/voice_search.dart';

const baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() => runApp(const JumuishaApp());

class GovernmentService {
  final String id, name, description, agency, officialUrl, status;
  GovernmentService.fromJson(Map<String, dynamic> json)
      : id = json['id'] as String,
        name = json['name'] as String,
        description = json['description'] as String,
        agency = json['agency'] as String,
        officialUrl = json['official_url'] as String,
        status = json['status'] as String;
}

class JumuishaApp extends StatefulWidget {
  const JumuishaApp({super.key});
  @override
  State<JumuishaApp> createState() => _JumuishaAppState();
}

class _JumuishaAppState extends State<JumuishaApp> {
  double scale = 1.0;
  bool highContrast = false;
  bool reduceMotion = true;
  bool easyRead = false;
  String language = 'English';
  final assistive = AssistiveController();
  final cache = PublicCatalogueCache();
  List<GovernmentService>? servicesCache;
  Future<List<GovernmentService>>? servicesFuture;

  @override
  void initState() {
    super.initState();
    servicesFuture = loadServicesCached();
  }

  Future<List<GovernmentService>> loadServicesCached() async {
    try {
      final data = await loadServices();
      await cache.save(jsonEncode(data.map((s) => {'id':s.id,'name':s.name,'description':s.description,'agency':s.agency,'official_url':s.officialUrl,'status':s.status}).toList()));
      return data;
    } catch (_) {
      final cached = await cache.load();
      if (cached == null) rethrow;
      final items = jsonDecode(cached) as List<dynamic>;
      return items.map((e) => GovernmentService.fromJson(e as Map<String, dynamic>)).toList();
    }
  }

  @override
  void dispose() {
    assistive.stop();
    super.dispose();
  }
  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xff126b68),
      brightness: highContrast ? Brightness.dark : Brightness.light,
    );
    return MaterialApp(
      title: 'Jumuisha AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: scheme,
        useMaterial3: true,
        visualDensity: VisualDensity.standard,
      ),
      builder: (context, child) => MediaQuery(
        data: MediaQuery.of(context).copyWith(
          textScaler: TextScaler.linear(scale),
          disableAnimations: reduceMotion,
        ),
        child: child!,
      ),
      home: Scaffold(
        appBar: AppBar(title: const Text('Jumuisha AI')),
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(18),
            children: [
              Text(
                language == 'Kiswahili'
                    ? 'Huduma za serikali kwa wote'
                    : 'Government services for everyone',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              const Text('Accessible service guidance. Government submissions are not enabled in this prototype.'),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: () => assistive.speak(
                  language == 'Kiswahili' ? 'Huduma za serikali kwa wote' : 'Government services for everyone',
                  language: language == 'Kiswahili' ? 'sw-KE' : 'en-US',
                ),
                icon: const Icon(Icons.volume_up),
                label: const Text('Read introduction aloud'),
              ),
              const SizedBox(height: 20),
              Semantics(
                header: true,
                child: Text('Your accessibility settings',
                    style: Theme.of(context).textTheme.titleLarge),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: language,
                decoration: const InputDecoration(
                  labelText: 'Interface language',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'English', child: Text('English')),
                  DropdownMenuItem(value: 'Kiswahili', child: Text('Kiswahili (preview)')),
                ],
                onChanged: (value) => setState(() => language = value ?? 'English'),
              ),
              const SizedBox(height: 8),
              Text('Text size: ${(scale * 100).round()}%'),
              Slider(
                value: scale,
                min: 1,
                max: 2,
                divisions: 4,
                label: '${(scale * 100).round()}%',
                onChanged: (value) => setState(() => scale = value),
              ),
              SwitchListTile(
                title: const Text('High contrast'),
                value: highContrast,
                onChanged: (v) => setState(() => highContrast = v),
              ),
              SwitchListTile(
                title: const Text('Reduce motion'),
                value: reduceMotion,
                onChanged: (v) => setState(() => reduceMotion = v),
              ),
              SwitchListTile(
                title: const Text('Easy Read'),
                subtitle: const Text('Shorter descriptions for easier navigation'),
                value: easyRead,
                onChanged: (v) => setState(() => easyRead = v),
              ),
              FilledButton.icon(
                icon: const Icon(Icons.mic),
                label: const Text('Search by voice or typing'),
                onPressed: () async {
                  final result = await Navigator.of(context).push<String>(
                    MaterialPageRoute(builder: (_) => const VoiceServiceSearch()),
                  );
                  if (!context.mounted || result == null || result.isEmpty) return;
                  final all = await servicesFuture;
                  if (!context.mounted || all == null) return;
                  final matches = all.where((service) =>
                    ('${service.name} ${service.description} ${service.agency}')
                      .toLowerCase().contains(result.toLowerCase())).toList();
                  await showDialog<void>(context: context, builder: (context) => AlertDialog(
                    title: const Text('Matching services'),
                    content: SizedBox(width: 420, child: ListView(shrinkWrap: true, children: [
                      if (matches.isEmpty) const Text('No matching service. Browse the directory.'),
                      for (final service in matches) ListTile(
                        title: Text(service.name),
                        onTap: () {Navigator.pop(context); Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => PublicServiceJourney(service:service)));},
                      ),
                    ])),
                    actions: [TextButton(onPressed: () => Navigator.pop(context),child: const Text('Close'))],
                  ));
                },
              ),
              const SizedBox(height: 18),
              Semantics(
                header: true,
                child: Text('Government services',
                    style: Theme.of(context).textTheme.titleLarge),
              ),
              const SizedBox(height: 8),
              FutureBuilder<List<GovernmentService>>(
                future: servicesFuture,
                builder: (context, snapshot) {
                  if (snapshot.hasError) {
                    return const Text('Unable to load services. Check the API connection. You may try again.');
                  }
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator(
                      semanticsLabel: 'Loading available services',
                    ));
                  }
                  return Column(
                    children: [
                      for (final service in snapshot.data!)
                        Card(
                          child: ListTile(
                            title: Text(service.name),
                            subtitle: Text(easyRead
                                ? service.agency
                                : '${service.agency}\n${service.description}'),
                            isThreeLine: !easyRead,
                            trailing: IconButton(
                              tooltip: 'Read service aloud',
                              onPressed: () => assistive.speak(service.name + '. ' + service.description,
                                language: language == 'Kiswahili' ? 'sw-KE' : 'en-US'),
                              icon: const Icon(Icons.volume_up),
                            ),
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) => PublicServiceJourney(service: service),
                              ),
                            ),
                          ),
                        ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 12),
              const Text(
                'Kenyan Sign Language: validated video and sprite assets will appear here when licensed and approved. Use a qualified interpreter for important official decisions.',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

Future<List<GovernmentService>> loadServices() async {
  final response = await http.get(
    Uri.parse('$baseUrl/services'),
  ).timeout(const Duration(seconds: 10));
  if (response.statusCode != 200) {
    throw Exception('Service directory unavailable');
  }
  final data = jsonDecode(response.body) as List<dynamic>;
  return data.map((e) => GovernmentService.fromJson(e as Map<String, dynamic>)).toList();
}
