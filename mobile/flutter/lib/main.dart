// ARQYV Flutter mobile client scaffold.
// Connect to the ARQYV desktop API server at localhost:8765.

import 'package:flutter/material.dart';

void main() {
  runApp(const ARQYVApp());
}

class ARQYVApp extends StatelessWidget {
  const ARQYVApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ARQYV',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF00B4D8),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _searchController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ARQYV'),
        actions: [
          IconButton(icon: const Icon(Icons.settings), onPressed: () {}),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: SearchBar(
              controller: _searchController,
              hintText: 'Search your library…',
              leading: const Icon(Icons.search),
              trailing: [
                IconButton(
                  icon: const Icon(Icons.mic),
                  onPressed: () {
                    // TODO: Voice search
                  },
                ),
              ],
            ),
          ),
          const Expanded(
            child: Center(
              child: Text(
                'ARQYV Mobile\nConnect to desktop app',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
          NavigationDestination(icon: Icon(Icons.play_circle), label: 'Player'),
          NavigationDestination(icon: Icon(Icons.cloud), label: 'Cloud'),
        ],
      ),
    );
  }
}
