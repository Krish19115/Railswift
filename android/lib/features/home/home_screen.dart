import 'package:flutter/material.dart';

import '../../core/models/health_status.dart';
import '../../core/services/health_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _healthService = HealthService();
  late final Future<HealthStatus> _health = _healthService.fetch();

  @override
  void dispose() {
    _healthService.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(22, 14, 22, 24),
          children: [
            Row(
              children: [
                Container(
                  width: 34,
                  height: 34,
                  decoration: const BoxDecoration(
                    color: Color(0xFF246D53),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(11),
                      topRight: Radius.circular(11),
                      bottomRight: Radius.circular(11),
                      bottomLeft: Radius.circular(4),
                    ),
                  ),
                  alignment: Alignment.center,
                  child: const Text('R', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
                ),
                const SizedBox(width: 10),
                Text('railswift', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                const Spacer(),
                CircleAvatar(
                  radius: 18,
                  backgroundColor: const Color(0xFFE9F0E9),
                  child: Text('K', style: TextStyle(color: colors.primary, fontWeight: FontWeight.w700)),
                ),
              ],
            ),
            const SizedBox(height: 58),
            Text('YOUR JOURNEY, THOUGHTFULLY PLANNED', style: TextStyle(color: colors.primary, fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1.4)),
            const SizedBox(height: 18),
            Text('A little more certainty\nfor the journey ahead.', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w700, height: 1.16, letterSpacing: -1)),
            const SizedBox(height: 16),
            Text('Find the right train, understand your options, and feel ready when it is time to book.', style: TextStyle(color: Colors.blueGrey.shade600, height: 1.6)),
            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: null,
              icon: const Icon(Icons.north_east, size: 17),
              label: const Text('Plan a journey'),
            ),
            const SizedBox(height: 4),
            Text('Journey search arrives in the next phase', style: TextStyle(color: Colors.blueGrey.shade400, fontSize: 11)),
            const SizedBox(height: 34),
            Container(
              height: 180,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(22),
                gradient: const LinearGradient(colors: [Color(0xFFEFF5E9), Color(0xFFDAE8D4)], begin: Alignment.topLeft, end: Alignment.bottomRight),
              ),
              child: Stack(
                children: [
                  Positioned(right: 35, top: 28, child: Container(width: 64, height: 64, decoration: const BoxDecoration(color: Color(0xFFE9BA78), shape: BoxShape.circle))),
                  Positioned(left: 22, top: 67, child: Chip(avatar: const Icon(Icons.route, size: 17), label: const Text('A better way forward'))),
                  Positioned(left: 28, bottom: 16, child: Text('From here to there', style: TextStyle(color: Colors.green.shade900, fontWeight: FontWeight.w600))),
                  Positioned(right: 24, bottom: 15, child: Icon(Icons.train, color: colors.primary, size: 35)),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Card(
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(17),
                child: FutureBuilder<HealthStatus>(
                  future: _health,
                  builder: (context, snapshot) {
                    final connected = snapshot.data?.status == 'ok';
                    final database = snapshot.data?.database == 'ok';
                    final title = connected ? 'Your RailSwift foundation is ready' : snapshot.connectionState == ConnectionState.waiting ? 'Connecting to RailSwift…' : 'Getting things ready';
                    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
                      const SizedBox(height: 6),
                      Text('Journey search and live railway data will arrive in upcoming phases.', style: TextStyle(color: Colors.blueGrey.shade500, fontSize: 12)),
                      const SizedBox(height: 15),
                      Wrap(spacing: 16, runSpacing: 8, children: [
                        _ServiceStatus(label: connected ? 'API online' : 'API starting', online: connected),
                        _ServiceStatus(label: database ? 'Database online' : 'Database pending', online: database),
                      ]),
                    ]);
                  },
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('BOOKING IS ALWAYS COMPLETED BY YOU ON THE OFFICIAL RAILWAY PLATFORM.', style: TextStyle(color: Colors.blueGrey.shade400, fontSize: 9, height: 1.5, letterSpacing: .5)),
          ],
        ),
      ),
    );
  }
}

class _ServiceStatus extends StatelessWidget {
  const _ServiceStatus({required this.label, required this.online});

  final String label;
  final bool online;

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(Icons.circle, size: 7, color: online ? const Color(0xFF50A777) : const Color(0xFFD9B076)),
        const SizedBox(width: 6),
        Text(label, style: TextStyle(color: Colors.blueGrey.shade600, fontSize: 11)),
      ]);
}
