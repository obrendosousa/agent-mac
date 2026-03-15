package ai.chappie.app.node

import ai.chappie.app.gateway.GatewaySession
import ai.chappie.app.protocol.ChappieCalendarCommand
import ai.chappie.app.protocol.ChappieCanvasA2UICommand
import ai.chappie.app.protocol.ChappieCanvasCommand
import ai.chappie.app.protocol.ChappieCameraCommand
import ai.chappie.app.protocol.ChappieContactsCommand
import ai.chappie.app.protocol.ChappieDeviceCommand
import ai.chappie.app.protocol.ChappieLocationCommand
import ai.chappie.app.protocol.ChappieMotionCommand
import ai.chappie.app.protocol.ChappieNotificationsCommand
import ai.chappie.app.protocol.ChappieSmsCommand
import ai.chappie.app.protocol.ChappieSystemCommand

class InvokeDispatcher(
  private val canvas: CanvasController,
  private val cameraHandler: CameraHandler,
  private val locationHandler: LocationHandler,
  private val deviceHandler: DeviceHandler,
  private val notificationsHandler: NotificationsHandler,
  private val systemHandler: SystemHandler,
  private val photosHandler: PhotosHandler,
  private val contactsHandler: ContactsHandler,
  private val calendarHandler: CalendarHandler,
  private val motionHandler: MotionHandler,
  private val smsHandler: SmsHandler,
  private val a2uiHandler: A2UIHandler,
  private val debugHandler: DebugHandler,
  private val isForeground: () -> Boolean,
  private val cameraEnabled: () -> Boolean,
  private val locationEnabled: () -> Boolean,
  private val smsAvailable: () -> Boolean,
  private val debugBuild: () -> Boolean,
  private val refreshNodeCanvasCapability: suspend () -> Boolean,
  private val onCanvasA2uiPush: () -> Unit,
  private val onCanvasA2uiReset: () -> Unit,
  private val motionActivityAvailable: () -> Boolean,
  private val motionPedometerAvailable: () -> Boolean,
) {
  suspend fun handleInvoke(command: String, paramsJson: String?): GatewaySession.InvokeResult {
    val spec =
      InvokeCommandRegistry.find(command)
        ?: return GatewaySession.InvokeResult.error(
          code = "INVALID_REQUEST",
          message = "INVALID_REQUEST: unknown command",
        )
    if (spec.requiresForeground && !isForeground()) {
      return GatewaySession.InvokeResult.error(
        code = "NODE_BACKGROUND_UNAVAILABLE",
        message = "NODE_BACKGROUND_UNAVAILABLE: canvas/camera/screen commands require foreground",
      )
    }
    availabilityError(spec.availability)?.let { return it }

    return when (command) {
      // Canvas commands
      ChappieCanvasCommand.Present.rawValue -> {
        val url = CanvasController.parseNavigateUrl(paramsJson)
        canvas.navigate(url)
        GatewaySession.InvokeResult.ok(null)
      }
      ChappieCanvasCommand.Hide.rawValue -> GatewaySession.InvokeResult.ok(null)
      ChappieCanvasCommand.Navigate.rawValue -> {
        val url = CanvasController.parseNavigateUrl(paramsJson)
        canvas.navigate(url)
        GatewaySession.InvokeResult.ok(null)
      }
      ChappieCanvasCommand.Eval.rawValue -> {
        val js =
          CanvasController.parseEvalJs(paramsJson)
            ?: return GatewaySession.InvokeResult.error(
              code = "INVALID_REQUEST",
              message = "INVALID_REQUEST: javaScript required",
            )
        withCanvasAvailable {
          val result = canvas.eval(js)
          GatewaySession.InvokeResult.ok("""{"result":${result.toJsonString()}}""")
        }
      }
      ChappieCanvasCommand.Snapshot.rawValue -> {
        val snapshotParams = CanvasController.parseSnapshotParams(paramsJson)
        withCanvasAvailable {
          val base64 =
            canvas.snapshotBase64(
              format = snapshotParams.format,
              quality = snapshotParams.quality,
              maxWidth = snapshotParams.maxWidth,
            )
          GatewaySession.InvokeResult.ok("""{"format":"${snapshotParams.format.rawValue}","base64":"$base64"}""")
        }
      }

      // A2UI commands
      ChappieCanvasA2UICommand.Reset.rawValue ->
        withReadyA2ui {
          withCanvasAvailable {
            val res = canvas.eval(A2UIHandler.a2uiResetJS)
            onCanvasA2uiReset()
            GatewaySession.InvokeResult.ok(res)
          }
        }
      ChappieCanvasA2UICommand.Push.rawValue, ChappieCanvasA2UICommand.PushJSONL.rawValue -> {
        val messages =
          try {
            a2uiHandler.decodeA2uiMessages(command, paramsJson)
          } catch (err: Throwable) {
            return GatewaySession.InvokeResult.error(
              code = "INVALID_REQUEST",
              message = err.message ?: "invalid A2UI payload"
            )
          }
        withReadyA2ui {
          withCanvasAvailable {
            val js = A2UIHandler.a2uiApplyMessagesJS(messages)
            val res = canvas.eval(js)
            onCanvasA2uiPush()
            GatewaySession.InvokeResult.ok(res)
          }
        }
      }

      // Camera commands
      ChappieCameraCommand.List.rawValue -> cameraHandler.handleList(paramsJson)
      ChappieCameraCommand.Snap.rawValue -> cameraHandler.handleSnap(paramsJson)
      ChappieCameraCommand.Clip.rawValue -> cameraHandler.handleClip(paramsJson)

      // Location command
      ChappieLocationCommand.Get.rawValue -> locationHandler.handleLocationGet(paramsJson)

      // Device commands
      ChappieDeviceCommand.Status.rawValue -> deviceHandler.handleDeviceStatus(paramsJson)
      ChappieDeviceCommand.Info.rawValue -> deviceHandler.handleDeviceInfo(paramsJson)
      ChappieDeviceCommand.Permissions.rawValue -> deviceHandler.handleDevicePermissions(paramsJson)
      ChappieDeviceCommand.Health.rawValue -> deviceHandler.handleDeviceHealth(paramsJson)

      // Notifications command
      ChappieNotificationsCommand.List.rawValue -> notificationsHandler.handleNotificationsList(paramsJson)
      ChappieNotificationsCommand.Actions.rawValue -> notificationsHandler.handleNotificationsActions(paramsJson)

      // System command
      ChappieSystemCommand.Notify.rawValue -> systemHandler.handleSystemNotify(paramsJson)

      // Photos command
      ai.chappie.app.protocol.ChappiePhotosCommand.Latest.rawValue -> photosHandler.handlePhotosLatest(
        paramsJson,
      )

      // Contacts command
      ChappieContactsCommand.Search.rawValue -> contactsHandler.handleContactsSearch(paramsJson)
      ChappieContactsCommand.Add.rawValue -> contactsHandler.handleContactsAdd(paramsJson)

      // Calendar command
      ChappieCalendarCommand.Events.rawValue -> calendarHandler.handleCalendarEvents(paramsJson)
      ChappieCalendarCommand.Add.rawValue -> calendarHandler.handleCalendarAdd(paramsJson)

      // Motion command
      ChappieMotionCommand.Activity.rawValue -> motionHandler.handleMotionActivity(paramsJson)
      ChappieMotionCommand.Pedometer.rawValue -> motionHandler.handleMotionPedometer(paramsJson)

      // SMS command
      ChappieSmsCommand.Send.rawValue -> smsHandler.handleSmsSend(paramsJson)

      // Debug commands
      "debug.ed25519" -> debugHandler.handleEd25519()
      "debug.logs" -> debugHandler.handleLogs()
      else -> GatewaySession.InvokeResult.error(code = "INVALID_REQUEST", message = "INVALID_REQUEST: unknown command")
    }
  }

  private suspend fun withReadyA2ui(
    block: suspend () -> GatewaySession.InvokeResult,
  ): GatewaySession.InvokeResult {
    var a2uiUrl = a2uiHandler.resolveA2uiHostUrl()
      ?: return GatewaySession.InvokeResult.error(
        code = "A2UI_HOST_NOT_CONFIGURED",
        message = "A2UI_HOST_NOT_CONFIGURED: gateway did not advertise canvas host",
      )
    val readyOnFirstCheck = a2uiHandler.ensureA2uiReady(a2uiUrl)
    if (!readyOnFirstCheck) {
      if (!refreshNodeCanvasCapability()) {
        return GatewaySession.InvokeResult.error(
          code = "A2UI_HOST_UNAVAILABLE",
          message = "A2UI_HOST_UNAVAILABLE: A2UI host not reachable",
        )
      }
      a2uiUrl = a2uiHandler.resolveA2uiHostUrl()
        ?: return GatewaySession.InvokeResult.error(
          code = "A2UI_HOST_NOT_CONFIGURED",
          message = "A2UI_HOST_NOT_CONFIGURED: gateway did not advertise canvas host",
        )
      if (!a2uiHandler.ensureA2uiReady(a2uiUrl)) {
        return GatewaySession.InvokeResult.error(
          code = "A2UI_HOST_UNAVAILABLE",
          message = "A2UI_HOST_UNAVAILABLE: A2UI host not reachable",
        )
      }
    }
    return block()
  }

  private suspend fun withCanvasAvailable(
    block: suspend () -> GatewaySession.InvokeResult,
  ): GatewaySession.InvokeResult {
    return try {
      block()
    } catch (_: Throwable) {
      GatewaySession.InvokeResult.error(
        code = "NODE_BACKGROUND_UNAVAILABLE",
        message = "NODE_BACKGROUND_UNAVAILABLE: canvas unavailable",
      )
    }
  }

  private fun availabilityError(availability: InvokeCommandAvailability): GatewaySession.InvokeResult? {
    return when (availability) {
      InvokeCommandAvailability.Always -> null
      InvokeCommandAvailability.CameraEnabled ->
        if (cameraEnabled()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "CAMERA_DISABLED",
            message = "CAMERA_DISABLED: enable Camera in Settings",
          )
        }
      InvokeCommandAvailability.LocationEnabled ->
        if (locationEnabled()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "LOCATION_DISABLED",
            message = "LOCATION_DISABLED: enable Location in Settings",
          )
        }
      InvokeCommandAvailability.MotionActivityAvailable ->
        if (motionActivityAvailable()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "MOTION_UNAVAILABLE",
            message = "MOTION_UNAVAILABLE: accelerometer not available",
          )
        }
      InvokeCommandAvailability.MotionPedometerAvailable ->
        if (motionPedometerAvailable()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "PEDOMETER_UNAVAILABLE",
            message = "PEDOMETER_UNAVAILABLE: step counter not available",
          )
        }
      InvokeCommandAvailability.SmsAvailable ->
        if (smsAvailable()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "SMS_UNAVAILABLE",
            message = "SMS_UNAVAILABLE: SMS not available on this device",
          )
        }
      InvokeCommandAvailability.DebugBuild ->
        if (debugBuild()) {
          null
        } else {
          GatewaySession.InvokeResult.error(
            code = "INVALID_REQUEST",
            message = "INVALID_REQUEST: unknown command",
          )
        }
    }
  }
}
