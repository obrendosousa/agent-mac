package ai.chappie.app.node

import ai.chappie.app.protocol.ChappieCalendarCommand
import ai.chappie.app.protocol.ChappieCameraCommand
import ai.chappie.app.protocol.ChappieCapability
import ai.chappie.app.protocol.ChappieContactsCommand
import ai.chappie.app.protocol.ChappieDeviceCommand
import ai.chappie.app.protocol.ChappieLocationCommand
import ai.chappie.app.protocol.ChappieMotionCommand
import ai.chappie.app.protocol.ChappieNotificationsCommand
import ai.chappie.app.protocol.ChappiePhotosCommand
import ai.chappie.app.protocol.ChappieSmsCommand
import ai.chappie.app.protocol.ChappieSystemCommand
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class InvokeCommandRegistryTest {
  private val coreCapabilities =
    setOf(
      ChappieCapability.Canvas.rawValue,
      ChappieCapability.Device.rawValue,
      ChappieCapability.Notifications.rawValue,
      ChappieCapability.System.rawValue,
      ChappieCapability.Photos.rawValue,
      ChappieCapability.Contacts.rawValue,
      ChappieCapability.Calendar.rawValue,
    )

  private val optionalCapabilities =
    setOf(
      ChappieCapability.Camera.rawValue,
      ChappieCapability.Location.rawValue,
      ChappieCapability.Sms.rawValue,
      ChappieCapability.VoiceWake.rawValue,
      ChappieCapability.Motion.rawValue,
    )

  private val coreCommands =
    setOf(
      ChappieDeviceCommand.Status.rawValue,
      ChappieDeviceCommand.Info.rawValue,
      ChappieDeviceCommand.Permissions.rawValue,
      ChappieDeviceCommand.Health.rawValue,
      ChappieNotificationsCommand.List.rawValue,
      ChappieNotificationsCommand.Actions.rawValue,
      ChappieSystemCommand.Notify.rawValue,
      ChappiePhotosCommand.Latest.rawValue,
      ChappieContactsCommand.Search.rawValue,
      ChappieContactsCommand.Add.rawValue,
      ChappieCalendarCommand.Events.rawValue,
      ChappieCalendarCommand.Add.rawValue,
    )

  private val optionalCommands =
    setOf(
      ChappieCameraCommand.Snap.rawValue,
      ChappieCameraCommand.Clip.rawValue,
      ChappieCameraCommand.List.rawValue,
      ChappieLocationCommand.Get.rawValue,
      ChappieMotionCommand.Activity.rawValue,
      ChappieMotionCommand.Pedometer.rawValue,
      ChappieSmsCommand.Send.rawValue,
    )

  private val debugCommands = setOf("debug.logs", "debug.ed25519")

  @Test
  fun advertisedCapabilities_respectsFeatureAvailability() {
    val capabilities = InvokeCommandRegistry.advertisedCapabilities(defaultFlags())

    assertContainsAll(capabilities, coreCapabilities)
    assertMissingAll(capabilities, optionalCapabilities)
  }

  @Test
  fun advertisedCapabilities_includesFeatureCapabilitiesWhenEnabled() {
    val capabilities =
      InvokeCommandRegistry.advertisedCapabilities(
        defaultFlags(
          cameraEnabled = true,
          locationEnabled = true,
          smsAvailable = true,
          voiceWakeEnabled = true,
          motionActivityAvailable = true,
          motionPedometerAvailable = true,
        ),
      )

    assertContainsAll(capabilities, coreCapabilities + optionalCapabilities)
  }

  @Test
  fun advertisedCommands_respectsFeatureAvailability() {
    val commands = InvokeCommandRegistry.advertisedCommands(defaultFlags())

    assertContainsAll(commands, coreCommands)
    assertMissingAll(commands, optionalCommands + debugCommands)
  }

  @Test
  fun advertisedCommands_includesFeatureCommandsWhenEnabled() {
    val commands =
      InvokeCommandRegistry.advertisedCommands(
        defaultFlags(
          cameraEnabled = true,
          locationEnabled = true,
          smsAvailable = true,
          motionActivityAvailable = true,
          motionPedometerAvailable = true,
          debugBuild = true,
        ),
      )

    assertContainsAll(commands, coreCommands + optionalCommands + debugCommands)
  }

  @Test
  fun advertisedCommands_onlyIncludesSupportedMotionCommands() {
    val commands =
      InvokeCommandRegistry.advertisedCommands(
        NodeRuntimeFlags(
          cameraEnabled = false,
          locationEnabled = false,
          smsAvailable = false,
          voiceWakeEnabled = false,
          motionActivityAvailable = true,
          motionPedometerAvailable = false,
          debugBuild = false,
        ),
      )

    assertTrue(commands.contains(ChappieMotionCommand.Activity.rawValue))
    assertFalse(commands.contains(ChappieMotionCommand.Pedometer.rawValue))
  }

  private fun defaultFlags(
    cameraEnabled: Boolean = false,
    locationEnabled: Boolean = false,
    smsAvailable: Boolean = false,
    voiceWakeEnabled: Boolean = false,
    motionActivityAvailable: Boolean = false,
    motionPedometerAvailable: Boolean = false,
    debugBuild: Boolean = false,
  ): NodeRuntimeFlags =
    NodeRuntimeFlags(
      cameraEnabled = cameraEnabled,
      locationEnabled = locationEnabled,
      smsAvailable = smsAvailable,
      voiceWakeEnabled = voiceWakeEnabled,
      motionActivityAvailable = motionActivityAvailable,
      motionPedometerAvailable = motionPedometerAvailable,
      debugBuild = debugBuild,
    )

  private fun assertContainsAll(actual: List<String>, expected: Set<String>) {
    expected.forEach { value -> assertTrue(actual.contains(value)) }
  }

  private fun assertMissingAll(actual: List<String>, forbidden: Set<String>) {
    forbidden.forEach { value -> assertFalse(actual.contains(value)) }
  }
}
