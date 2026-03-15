package ai.chappie.app.protocol

import org.junit.Assert.assertEquals
import org.junit.Test

class ChappieProtocolConstantsTest {
  @Test
  fun canvasCommandsUseStableStrings() {
    assertEquals("canvas.present", ChappieCanvasCommand.Present.rawValue)
    assertEquals("canvas.hide", ChappieCanvasCommand.Hide.rawValue)
    assertEquals("canvas.navigate", ChappieCanvasCommand.Navigate.rawValue)
    assertEquals("canvas.eval", ChappieCanvasCommand.Eval.rawValue)
    assertEquals("canvas.snapshot", ChappieCanvasCommand.Snapshot.rawValue)
  }

  @Test
  fun a2uiCommandsUseStableStrings() {
    assertEquals("canvas.a2ui.push", ChappieCanvasA2UICommand.Push.rawValue)
    assertEquals("canvas.a2ui.pushJSONL", ChappieCanvasA2UICommand.PushJSONL.rawValue)
    assertEquals("canvas.a2ui.reset", ChappieCanvasA2UICommand.Reset.rawValue)
  }

  @Test
  fun capabilitiesUseStableStrings() {
    assertEquals("canvas", ChappieCapability.Canvas.rawValue)
    assertEquals("camera", ChappieCapability.Camera.rawValue)
    assertEquals("voiceWake", ChappieCapability.VoiceWake.rawValue)
    assertEquals("location", ChappieCapability.Location.rawValue)
    assertEquals("sms", ChappieCapability.Sms.rawValue)
    assertEquals("device", ChappieCapability.Device.rawValue)
    assertEquals("notifications", ChappieCapability.Notifications.rawValue)
    assertEquals("system", ChappieCapability.System.rawValue)
    assertEquals("photos", ChappieCapability.Photos.rawValue)
    assertEquals("contacts", ChappieCapability.Contacts.rawValue)
    assertEquals("calendar", ChappieCapability.Calendar.rawValue)
    assertEquals("motion", ChappieCapability.Motion.rawValue)
  }

  @Test
  fun cameraCommandsUseStableStrings() {
    assertEquals("camera.list", ChappieCameraCommand.List.rawValue)
    assertEquals("camera.snap", ChappieCameraCommand.Snap.rawValue)
    assertEquals("camera.clip", ChappieCameraCommand.Clip.rawValue)
  }

  @Test
  fun notificationsCommandsUseStableStrings() {
    assertEquals("notifications.list", ChappieNotificationsCommand.List.rawValue)
    assertEquals("notifications.actions", ChappieNotificationsCommand.Actions.rawValue)
  }

  @Test
  fun deviceCommandsUseStableStrings() {
    assertEquals("device.status", ChappieDeviceCommand.Status.rawValue)
    assertEquals("device.info", ChappieDeviceCommand.Info.rawValue)
    assertEquals("device.permissions", ChappieDeviceCommand.Permissions.rawValue)
    assertEquals("device.health", ChappieDeviceCommand.Health.rawValue)
  }

  @Test
  fun systemCommandsUseStableStrings() {
    assertEquals("system.notify", ChappieSystemCommand.Notify.rawValue)
  }

  @Test
  fun photosCommandsUseStableStrings() {
    assertEquals("photos.latest", ChappiePhotosCommand.Latest.rawValue)
  }

  @Test
  fun contactsCommandsUseStableStrings() {
    assertEquals("contacts.search", ChappieContactsCommand.Search.rawValue)
    assertEquals("contacts.add", ChappieContactsCommand.Add.rawValue)
  }

  @Test
  fun calendarCommandsUseStableStrings() {
    assertEquals("calendar.events", ChappieCalendarCommand.Events.rawValue)
    assertEquals("calendar.add", ChappieCalendarCommand.Add.rawValue)
  }

  @Test
  fun motionCommandsUseStableStrings() {
    assertEquals("motion.activity", ChappieMotionCommand.Activity.rawValue)
    assertEquals("motion.pedometer", ChappieMotionCommand.Pedometer.rawValue)
  }
}
