import Foundation

// Stable identifier used for both the macOS LaunchAgent label and Nix-managed defaults suite.
// nix-chappie writes app defaults into this suite to survive app bundle identifier churn.
let launchdLabel = "ai.chappie.mac"
let gatewayLaunchdLabel = "ai.chappie.gateway"
let onboardingVersionKey = "chappie.onboardingVersion"
let onboardingSeenKey = "chappie.onboardingSeen"
let currentOnboardingVersion = 7
let pauseDefaultsKey = "chappie.pauseEnabled"
let iconAnimationsEnabledKey = "chappie.iconAnimationsEnabled"
let swabbleEnabledKey = "chappie.swabbleEnabled"
let swabbleTriggersKey = "chappie.swabbleTriggers"
let voiceWakeTriggerChimeKey = "chappie.voiceWakeTriggerChime"
let voiceWakeSendChimeKey = "chappie.voiceWakeSendChime"
let showDockIconKey = "chappie.showDockIcon"
let defaultVoiceWakeTriggers = ["chappie"]
let voiceWakeMaxWords = 32
let voiceWakeMaxWordLength = 64
let voiceWakeMicKey = "chappie.voiceWakeMicID"
let voiceWakeMicNameKey = "chappie.voiceWakeMicName"
let voiceWakeLocaleKey = "chappie.voiceWakeLocaleID"
let voiceWakeAdditionalLocalesKey = "chappie.voiceWakeAdditionalLocaleIDs"
let voicePushToTalkEnabledKey = "chappie.voicePushToTalkEnabled"
let talkEnabledKey = "chappie.talkEnabled"
let iconOverrideKey = "chappie.iconOverride"
let connectionModeKey = "chappie.connectionMode"
let remoteTargetKey = "chappie.remoteTarget"
let remoteIdentityKey = "chappie.remoteIdentity"
let remoteProjectRootKey = "chappie.remoteProjectRoot"
let remoteCliPathKey = "chappie.remoteCliPath"
let canvasEnabledKey = "chappie.canvasEnabled"
let cameraEnabledKey = "chappie.cameraEnabled"
let systemRunPolicyKey = "chappie.systemRunPolicy"
let systemRunAllowlistKey = "chappie.systemRunAllowlist"
let systemRunEnabledKey = "chappie.systemRunEnabled"
let locationModeKey = "chappie.locationMode"
let locationPreciseKey = "chappie.locationPreciseEnabled"
let peekabooBridgeEnabledKey = "chappie.peekabooBridgeEnabled"
let deepLinkKeyKey = "chappie.deepLinkKey"
let modelCatalogPathKey = "chappie.modelCatalogPath"
let modelCatalogReloadKey = "chappie.modelCatalogReload"
let cliInstallPromptedVersionKey = "chappie.cliInstallPromptedVersion"
let heartbeatsEnabledKey = "chappie.heartbeatsEnabled"
let debugPaneEnabledKey = "chappie.debugPaneEnabled"
let debugFileLogEnabledKey = "chappie.debug.fileLogEnabled"
let appLogLevelKey = "chappie.debug.appLogLevel"
let voiceWakeSupported: Bool = ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 26
