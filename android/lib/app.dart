import 'package:flutter/material.dart';

import 'features/home/home_screen.dart';

class RailSwiftApp extends StatelessWidget {
  const RailSwiftApp({super.key});

  @override
  Widget build(BuildContext context) {
    const forest = Color(0xFF246D53);
    return MaterialApp(
      title: 'RailSwift',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: forest),
        scaffoldBackgroundColor: const Color(0xFFF5F7F3),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
