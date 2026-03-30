import 'dart:async';
import '../models/api_models.dart';
import 'api_service.dart';

class GenerationService {
  final ApiService _api;

  GenerationService(this._api);

  /// Polls /status/{jobId} every 3 seconds until done or failed.
  Stream<JobStatus> pollStatus(String jobId) async* {
    while (true) {
      await Future.delayed(const Duration(seconds: 3));
      try {
        final status = await _api.getStatus(jobId);
        yield status;
        if (status.isDone || status.isFailed) break;
      } catch (_) {
        // Network blip — keep polling
      }
    }
  }

  /// Full flow: submit request, poll, return final status.
  Stream<JobStatus> generate(GenerateRequest request) async* {
    final jobId = await _api.generate(request);

    yield JobStatus(
      jobId: jobId,
      status: 'pending',
      progress: 0.02,
      stage: 'Job queued…',
    );

    await for (final status in pollStatus(jobId)) {
      yield status;
    }
  }
}
