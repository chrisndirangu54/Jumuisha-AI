import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

/// Only accepts URLs from reviewed, licensed, human KSL recordings.
class KslPlayer extends StatefulWidget {
  final Uri? approvedAsset;
  final String caption;
  final bool reviewed;
  const KslPlayer({super.key,required this.approvedAsset,required this.caption,required this.reviewed});
  @override
  State<KslPlayer> createState()=>_KslPlayerState();
}
class _KslPlayerState extends State<KslPlayer> {
  VideoPlayerController? video;
  String? error;
  @override
  void initState(){super.initState();start();}
  Future<void> start() async {
    final uri=widget.approvedAsset;
    if(!widget.reviewed||uri==null||uri.scheme!='https'){
      setState(()=>error='No human-reviewed KSL recording available. Read the caption or request an interpreter.');
      return;
    }
    try {
      final v=VideoPlayerController.networkUrl(uri);
      await v.initialize();
      await v.setLooping(true);
      if(!mounted){await v.dispose();return;}
      setState(()=>video=v);
    } catch (_) {
      if(mounted)setState(()=>error='Recording unavailable. Use the text alternative.');
    }
  }
  @override
  void dispose(){video?.dispose();super.dispose();}
  @override
  Widget build(BuildContext context)=>Column(children:[
    if(video!=null&&video!.value.isInitialized)
      AspectRatio(aspectRatio:video!.value.aspectRatio,child:VideoPlayer(video!)),
    if(error!=null) Text(error!),
    const SizedBox(height:10),
    Text(widget.caption),
    if(video!=null) IconButton(
      tooltip:video!.value.isPlaying?'Pause signing video':'Play signing video',
      onPressed:(){setState((){video!.value.isPlaying?video!.pause():video!.play();});},
      icon:Icon(video!.value.isPlaying?Icons.pause:Icons.play_arrow),
    ),
  ]);
}
