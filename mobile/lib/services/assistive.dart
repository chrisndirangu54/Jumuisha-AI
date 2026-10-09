import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Read-only assistive features. System screen readers / Braille are supported
/// through the OS accessibility tree, not through a fabricated Braille renderer.
class AssistiveController {
  final FlutterTts tts = FlutterTts();
  Future<void> speak(String text, {String language = 'en-US'}) async {
    await tts.setLanguage(language);
    await tts.setSpeechRate(0.46);
    await tts.speak(text);
  }
  Future<void> stop() => tts.stop();
}

class PublicCatalogueCache {
  static const key = 'public_services_catalogue_v1';
  Future<void> save(String payload) async {
    final store = await SharedPreferences.getInstance();
    await store.setString(key, payload);
  }
  Future<String?> load() async {
    final store = await SharedPreferences.getInstance();
    return store.getString(key);
  }
  Future<void> clear() async {
    final store = await SharedPreferences.getInstance();
    await store.remove(key);
  }
}
