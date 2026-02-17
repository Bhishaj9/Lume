class LumeLinkModel {
  const LumeLinkModel({
    required this.title,
    required this.url,
    required this.seeds,
  });

  final String title;
  final String url;
  final int seeds;

  bool get isHealthy => seeds > 0 && url.startsWith('magnet:');

  factory LumeLinkModel.fromJson(Map<String, dynamic> json) {
    return LumeLinkModel(
      title: json['title'] as String? ?? 'Unknown',
      url: json['url'] as String? ?? '',
      seeds: (json['seeds'] as num?)?.toInt() ?? 0,
    );
  }
}
