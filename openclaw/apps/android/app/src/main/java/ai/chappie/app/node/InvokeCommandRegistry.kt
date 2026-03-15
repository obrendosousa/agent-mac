package ai.chappie.app.node

import ai.chappie.app.protocol.ChappieCalendarCommand
import ai.chappie.app.protocol.ChappieCanvasA2UICommand
import ai.chappie.app.protocol.ChappieCanvasCommand
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

data class NodeRuntimeFlags(
  val cameraEnabled: Boolean,
  val locationEnabled: Boolean,
  val smsAvailable: Boolean,
  val voiceWakeEnabled: Boolean,
  val motionActivityAvailable: Boolean,
  val motionPedometerAvailable: Boolean,
  val debugBuild: Boolean,
)

enum class InvokeCommandAvailability {
  Always,
  CameraEnabled,
  LocationEnabled,
  SmsAvailable,
  MotionActivityAvailable,
  MotionPedometerAvailable,
  DebugBuild,
}

enum class NodeCapabilityAvailability {
  Always,
  CameraEnabled,
  LocationEnabled,
  SmsAvailable,
  VoiceWakeEnabled,
  MotionAvailable,
}

data class NodeCapabilitySpec(
  val name: String,
  val availability: NodeCapabilityAvailability = NodeCapabilityAvailability.Always,
)

data class InvokeCommandSpec(
  val name: String,
  val requiresForeground: Boolean = false,
  val availability: InvokeCommandAvailability = InvokeCommandAvailability.Always,
)

object InvokeCommandRegistry {
  val capabilityManifest: List<NodeCapabilitySpec> =
    listOf(
      NodeCapabilitySpec(name = ChappieCapability.Canvas.rawValue),
      NodeCapabilitySpec(name = ChappieCapability.Device.rawValue),
      NodeCapabilitySpec(name = ChappieCapability.Notifications.rawValue),
      NodeCapabilitySpec(name = ChappieCapability.System.rawValue),
      NodeCapabilitySpec(
        name = ChappieCapability.Camera.rawValue,
        availability = NodeCapabilityAvailability.CameraEnabled,
      ),
      NodeCapabilitySpec(
        name = ChappieCapability.Sms.rawValue,
        availability = NodeCapabilityAvailability.SmsAvailable,
      ),
      NodeCapabilitySpec(
        name = ChappieCapability.VoiceWake.rawValue,
        availability = NodeCapabilityAvailability.VoiceWakeEnabled,
      ),
      NodeCapabilitySpec(
        name = ChappieCapability.Location.rawValue,
        availability = NodeCapabilityAvailability.LocationEnabled,
      ),
      NodeCapabilitySpec(name = ChappieCapability.Photos.rawValue),
      NodeCapabilitySpec(name = ChappieCapability.Contacts.rawValue),
      NodeCapabilitySpec(name = ChappieCapability.Calendar.rawValue),
      NodeCapabilitySpec(
        name = ChappieCapability.Motion.rawValue,
        availability = NodeCapabilityAvailability.MotionAvailable,
      ),
    )

  val all: List<InvokeCommandSpec> =
    listOf(
      InvokeCommandSpec(
        name = ChappieCanvasCommand.Present.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasCommand.Hide.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasCommand.Navigate.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasCommand.Eval.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasCommand.Snapshot.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasA2UICommand.Push.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasA2UICommand.PushJSONL.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieCanvasA2UICommand.Reset.rawValue,
        requiresForeground = true,
      ),
      InvokeCommandSpec(
        name = ChappieSystemCommand.Notify.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieCameraCommand.List.rawValue,
        requiresForeground = true,
        availability = InvokeCommandAvailability.CameraEnabled,
      ),
      InvokeCommandSpec(
        name = ChappieCameraCommand.Snap.rawValue,
        requiresForeground = true,
        availability = InvokeCommandAvailability.CameraEnabled,
      ),
      InvokeCommandSpec(
        name = ChappieCameraCommand.Clip.rawValue,
        requiresForeground = true,
        availability = InvokeCommandAvailability.CameraEnabled,
      ),
      InvokeCommandSpec(
        name = ChappieLocationCommand.Get.rawValue,
        availability = InvokeCommandAvailability.LocationEnabled,
      ),
      InvokeCommandSpec(
        name = ChappieDeviceCommand.Status.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieDeviceCommand.Info.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieDeviceCommand.Permissions.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieDeviceCommand.Health.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieNotificationsCommand.List.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieNotificationsCommand.Actions.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappiePhotosCommand.Latest.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieContactsCommand.Search.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieContactsCommand.Add.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieCalendarCommand.Events.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieCalendarCommand.Add.rawValue,
      ),
      InvokeCommandSpec(
        name = ChappieMotionCommand.Activity.rawValue,
        availability = InvokeCommandAvailability.MotionActivityAvailable,
      ),
      InvokeCommandSpec(
        name = ChappieMotionCommand.Pedometer.rawValue,
        availability = InvokeCommandAvailability.MotionPedometerAvailable,
      ),
      InvokeCommandSpec(
        name = ChappieSmsCommand.Send.rawValue,
        availability = InvokeCommandAvailability.SmsAvailable,
      ),
      InvokeCommandSpec(
        name = "debug.logs",
        availability = InvokeCommandAvailability.DebugBuild,
      ),
      InvokeCommandSpec(
        name = "debug.ed25519",
        availability = InvokeCommandAvailability.DebugBuild,
      ),
    )

  private val byNameInternal: Map<String, InvokeCommandSpec> = all.associateBy { it.name }

  fun find(command: String): InvokeCommandSpec? = byNameInternal[command]

  fun advertisedCapabilities(flags: NodeRuntimeFlags): List<String> {
    return capabilityManifest
      .filter { spec ->
        when (spec.availability) {
          NodeCapabilityAvailability.Always -> true
          NodeCapabilityAvailability.CameraEnabled -> flags.cameraEnabled
          NodeCapabilityAvailability.LocationEnabled -> flags.locationEnabled
          NodeCapabilityAvailability.SmsAvailable -> flags.smsAvailable
          NodeCapabilityAvailability.VoiceWakeEnabled -> flags.voiceWakeEnabled
          NodeCapabilityAvailability.MotionAvailable -> flags.motionActivityAvailable || flags.motionPedometerAvailable
        }
      }
      .map { it.name }
  }

  fun advertisedCommands(flags: NodeRuntimeFlags): List<String> {
    return all
      .filter { spec ->
        when (spec.availability) {
          InvokeCommandAvailability.Always -> true
          InvokeCommandAvailability.CameraEnabled -> flags.cameraEnabled
          InvokeCommandAvailability.LocationEnabled -> flags.locationEnabled
          InvokeCommandAvailability.SmsAvailable -> flags.smsAvailable
          InvokeCommandAvailability.MotionActivityAvailable -> flags.motionActivityAvailable
          InvokeCommandAvailability.MotionPedometerAvailable -> flags.motionPedometerAvailable
          InvokeCommandAvailability.DebugBuild -> flags.debugBuild
        }
      }
      .map { it.name }
  }
}
