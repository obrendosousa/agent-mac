import Foundation

public enum ChappieCameraCommand: String, Codable, Sendable {
    case list = "camera.list"
    case snap = "camera.snap"
    case clip = "camera.clip"
}

public enum ChappieCameraFacing: String, Codable, Sendable {
    case back
    case front
}

public enum ChappieCameraImageFormat: String, Codable, Sendable {
    case jpg
    case jpeg
}

public enum ChappieCameraVideoFormat: String, Codable, Sendable {
    case mp4
}

public struct ChappieCameraSnapParams: Codable, Sendable, Equatable {
    public var facing: ChappieCameraFacing?
    public var maxWidth: Int?
    public var quality: Double?
    public var format: ChappieCameraImageFormat?
    public var deviceId: String?
    public var delayMs: Int?

    public init(
        facing: ChappieCameraFacing? = nil,
        maxWidth: Int? = nil,
        quality: Double? = nil,
        format: ChappieCameraImageFormat? = nil,
        deviceId: String? = nil,
        delayMs: Int? = nil)
    {
        self.facing = facing
        self.maxWidth = maxWidth
        self.quality = quality
        self.format = format
        self.deviceId = deviceId
        self.delayMs = delayMs
    }
}

public struct ChappieCameraClipParams: Codable, Sendable, Equatable {
    public var facing: ChappieCameraFacing?
    public var durationMs: Int?
    public var includeAudio: Bool?
    public var format: ChappieCameraVideoFormat?
    public var deviceId: String?

    public init(
        facing: ChappieCameraFacing? = nil,
        durationMs: Int? = nil,
        includeAudio: Bool? = nil,
        format: ChappieCameraVideoFormat? = nil,
        deviceId: String? = nil)
    {
        self.facing = facing
        self.durationMs = durationMs
        self.includeAudio = includeAudio
        self.format = format
        self.deviceId = deviceId
    }
}
