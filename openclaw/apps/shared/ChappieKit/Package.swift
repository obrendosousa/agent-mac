// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "ChappieKit",
    platforms: [
        .iOS(.v18),
        .macOS(.v15),
    ],
    products: [
        .library(name: "ChappieProtocol", targets: ["ChappieProtocol"]),
        .library(name: "ChappieKit", targets: ["ChappieKit"]),
        .library(name: "ChappieChatUI", targets: ["ChappieChatUI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/chappie-team/ElevenLabsKit", exact: "0.1.0"),
        .package(url: "https://github.com/gonzalezreal/textual", exact: "0.3.1"),
    ],
    targets: [
        .target(
            name: "ChappieProtocol",
            path: "Sources/ChappieProtocol",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ChappieKit",
            dependencies: [
                "ChappieProtocol",
                .product(name: "ElevenLabsKit", package: "ElevenLabsKit"),
            ],
            path: "Sources/ChappieKit",
            resources: [
                .process("Resources"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ChappieChatUI",
            dependencies: [
                "ChappieKit",
                .product(
                    name: "Textual",
                    package: "textual",
                    condition: .when(platforms: [.macOS, .iOS])),
            ],
            path: "Sources/ChappieChatUI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "ChappieKitTests",
            dependencies: ["ChappieKit", "ChappieChatUI"],
            path: "Tests/ChappieKitTests",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
