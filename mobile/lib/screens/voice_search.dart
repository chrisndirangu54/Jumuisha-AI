import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import '../main.dart';

/// Device speech recognition: availability and languages depend on installed OS engines.
/// No audio is sent to the Jumuisha API; platform recognition may be cloud-based.
class VoiceServiceSearch extends StatefulWidget {
  const VoiceServiceSearch({super.key});
  @override
  State<VoiceServiceSearch> createState() => _VoiceServiceSearchState();
}
class _VoiceServiceSearchState extends State<VoiceServiceSearch> {
  final engine=stt.SpeechToText();
  final query=TextEditingController();
  bool listening=false;
  String status='Speak or type a service name. You can edit the text.';
  Future<void> listen() async {
    final available=await engine.initialize(
      onStatus:(value) {if(mounted) setState(()=>status='Speech status: $value');},
      onError:(error) {if(mounted) setState(()=>status='Speech input unavailable: ${error.errorMsg}');},
    );
    if(!available) {if(mounted) setState(()=>status='Speech input unavailable. Use the keyboard.');return;}
    final locales=await engine.locales();
    final sw=locales.where((l)=>l.localeId.toLowerCase().startsWith('sw')).toList();
    await engine.listen(
      localeId:sw.isNotEmpty?sw.first.localeId:null,
      onResult:(result) {if(mounted) setState(()=>query.text=result.recognizedWords);},
    );
    if(mounted) setState(()=>listening=true);
  }
  @override
  void dispose(){engine.cancel();query.dispose();super.dispose();}
  @override
  Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text('Voice and text search')),
    body:ListView(padding:const EdgeInsets.all(20),children:[
      const Text('Speech recognition may use your device provider. Avoid speaking sensitive information.'),
      const SizedBox(height:12),
      TextField(controller:query,decoration:const InputDecoration(labelText:'Government service',border:OutlineInputBorder())),
      const SizedBox(height:12),
      FilledButton.icon(
        onPressed:() async {if(listening){await engine.stop();setState(()=>listening=false);}else{await listen();}},
        icon:Icon(listening?Icons.stop:Icons.mic),
        label:Text(listening?'Stop listening':'Speak service name'),
      ),
      Semantics(liveRegion:true,child:Text(status)),
      const SizedBox(height:16),
      FilledButton(
        onPressed:()=>Navigator.pop(context,query.text.trim()),
        child:const Text('Use this search'),
      )
    ]),
  );
}
