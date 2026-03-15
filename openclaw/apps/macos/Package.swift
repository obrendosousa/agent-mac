// swift-tools-version: 6.2
// Package manifest for the Chappie macOS companion (menu bar app + IPC library).

import PackageDescription

let package = Package(
    name: "Chappie",
    platforms: [
        .macOS(.v15),
    ],
    products: [
        .library(name: "ChappieIPC", targets: ["ChappieIPC"]),
        .library(name: "ChappieDiscovery", targets: ["ChappieDiscovery"]),
        .executable(name: "Chappie", targets: ["Chappie"]),
        .executable(name: "chappie-mac", targets: ["ChappieMacCLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/orchetect/MenuBarExtraAccess", exact: "1.2.2"),
        .package(url: "https://github.com/swiftlang/swift-subprocess.git", from: "0.1.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.8.0"),
        .package(url: "https://github.com/sparkle-project/Sparkle", from: "2.8.1"),
        .package(url: "https://github.com/chappie-team/Peekaboo.git", branch: "main"),
        .package(path: "../shared/ChappieKit"),
        .package(path: "../../Swabble"),
    ],
    targets: [
        .target(
            name: "ChappieIPC",
            dependencies: [],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ChappieDiscovery",
            dependencies: [
                .product(name: "ChappieKit", package: "ChappieKit"),
            ],
            path: "Sources/ChappieDiscovery",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "Chappie",
            dependencies: [
                "ChappieIPC",
                "ChappieDiscovery",
                .product(name: "ChappieKit", package: "ChappieKit"),
                .product(name: "ChappieChatUI", package: "ChappieKit"),
                .product(name: "ChappieProtocol", package: "ChappieKit"),
                .product(name: "SwabbleKit", package: "swabble"),
                .product(name: "MenuBarExtraAccess", package: "MenuBarExtraAccess"),
                .product(name: "Subprocess", package: "swift-subprocess"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Sparkle", package: "Sparkle"),
                .product(name: "PeekabooBridge", package: "Peekaboo"),
                .product(name: "PeekabooAutomationKit", package: "Peekaboo"),
            ],
            exclude: [
                "Resources/Info.plist",
            ],
            resources: [
                .copy("Resources/Chappie.icns"),
                .copy("Resources/DeviceModels"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "ChappieMacCLI",
            dependencies: [
                "ChappieDiscovery",
                .product(name: "ChappieKit", package: "ChappieKit"),
                .product(name: "ChappieProtocol", package: "ChappieKit"),
            ],
            path: "Sources/ChappieMacCLI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "ChappieIPCTests",
            dependencies: [
                "ChappieIPC",
                "Chappie",
                "ChappieDiscovery",
                .product(name: "ChappieProtocol", package: "ChappieKit"),
                .product(name: "SwabbleKit", package: "swabble"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
