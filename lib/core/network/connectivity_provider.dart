import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final connectivityProvider = Provider<Connectivity>((ref) => Connectivity());

final internetStatusProvider = StreamProvider.autoDispose<bool>((ref) {
  final connectivity = ref.watch(connectivityProvider);

  Future<bool> mapResult(List<ConnectivityResult> results) async {
    return results.any((result) => result != ConnectivityResult.none);
  }

  final controller = StreamController<bool>();

  connectivity.checkConnectivity().then((results) async {
    controller.add(await mapResult(results));
  });

  final sub = connectivity.onConnectivityChanged.listen((results) async {
    controller.add(await mapResult(results));
  });

  ref.onDispose(() async {
    await sub.cancel();
    await controller.close();
  });

  return controller.stream;
});
