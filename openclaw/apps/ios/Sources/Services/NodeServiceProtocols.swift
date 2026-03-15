import CoreLocation
import Foundation
import ChappieKit
import UIKit

typealias ChappieCameraSnapResult = (format: String, base64: String, width: Int, height: Int)
typealias ChappieCameraClipResult = (format: String, base64: String, durationMs: Int, hasAudio: Bool)

protocol CameraServicing: Sendable {
    func listDevices() async -> [CameraController.CameraDeviceInfo]
    func snap(params: ChappieCameraSnapParams) async throws -> ChappieCameraSnapResult
    func clip(params: ChappieCameraClipParams) async throws -> ChappieCameraClipResult
}

protocol ScreenRecordingServicing: Sendable {
    func record(
        screenIndex: Int?,
        durationMs: Int?,
        fps: Double?,
        includeAudio: Bool?,
        outPath: String?) async throws -> String
}

@MainActor
protocol LocationServicing: Sendable {
    func authorizationStatus() -> CLAuthorizationStatus
    func accuracyAuthorization() -> CLAccuracyAuthorization
    func ensureAuthorization(mode: ChappieLocationMode) async -> CLAuthorizationStatus
    func currentLocation(
        params: ChappieLocationGetParams,
        desiredAccuracy: ChappieLocationAccuracy,
        maxAgeMs: Int?,
        timeoutMs: Int?) async throws -> CLLocation
    func startLocationUpdates(
        desiredAccuracy: ChappieLocationAccuracy,
        significantChangesOnly: Bool) -> AsyncStream<CLLocation>
    func stopLocationUpdates()
    func startMonitoringSignificantLocationChanges(onUpdate: @escaping @Sendable (CLLocation) -> Void)
    func stopMonitoringSignificantLocationChanges()
}

@MainActor
protocol DeviceStatusServicing: Sendable {
    func status() async throws -> ChappieDeviceStatusPayload
    func info() -> ChappieDeviceInfoPayload
}

protocol PhotosServicing: Sendable {
    func latest(params: ChappiePhotosLatestParams) async throws -> ChappiePhotosLatestPayload
}

protocol ContactsServicing: Sendable {
    func search(params: ChappieContactsSearchParams) async throws -> ChappieContactsSearchPayload
    func add(params: ChappieContactsAddParams) async throws -> ChappieContactsAddPayload
}

protocol CalendarServicing: Sendable {
    func events(params: ChappieCalendarEventsParams) async throws -> ChappieCalendarEventsPayload
    func add(params: ChappieCalendarAddParams) async throws -> ChappieCalendarAddPayload
}

protocol RemindersServicing: Sendable {
    func list(params: ChappieRemindersListParams) async throws -> ChappieRemindersListPayload
    func add(params: ChappieRemindersAddParams) async throws -> ChappieRemindersAddPayload
}

protocol MotionServicing: Sendable {
    func activities(params: ChappieMotionActivityParams) async throws -> ChappieMotionActivityPayload
    func pedometer(params: ChappiePedometerParams) async throws -> ChappiePedometerPayload
}

struct WatchMessagingStatus: Sendable, Equatable {
    var supported: Bool
    var paired: Bool
    var appInstalled: Bool
    var reachable: Bool
    var activationState: String
}

struct WatchQuickReplyEvent: Sendable, Equatable {
    var replyId: String
    var promptId: String
    var actionId: String
    var actionLabel: String?
    var sessionKey: String?
    var note: String?
    var sentAtMs: Int?
    var transport: String
}

struct WatchNotificationSendResult: Sendable, Equatable {
    var deliveredImmediately: Bool
    var queuedForDelivery: Bool
    var transport: String
}

protocol WatchMessagingServicing: AnyObject, Sendable {
    func status() async -> WatchMessagingStatus
    func setReplyHandler(_ handler: (@Sendable (WatchQuickReplyEvent) -> Void)?)
    func sendNotification(
        id: String,
        params: ChappieWatchNotifyParams) async throws -> WatchNotificationSendResult
}

extension CameraController: CameraServicing {}
extension ScreenRecordService: ScreenRecordingServicing {}
extension LocationService: LocationServicing {}
