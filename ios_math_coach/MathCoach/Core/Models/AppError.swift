import Foundation

enum AppError: LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case server(statusCode: Int, message: String)
    case encodingFailed
    case decodingFailed
    case missingToken
    case missingProblemImage
    case emptyDrawing
    case message(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid backend URL."
        case .invalidResponse:
            return "The backend response was invalid."
        case .unauthorized:
            return "Session expired. Please log in again."
        case let .server(statusCode, message):
            return "Request failed (\(statusCode)): \(message)"
        case .encodingFailed:
            return "Failed to encode request."
        case .decodingFailed:
            return "Failed to decode server response."
        case .missingToken:
            return "No access token found."
        case .missingProblemImage:
            return "Please add a problem image before submitting."
        case .emptyDrawing:
            return "Please write at least one solution step before submitting."
        case let .message(message):
            return message
        }
    }
}
