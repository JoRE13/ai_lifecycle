import Foundation

enum QueryMode: String, CaseIterable, Identifiable, Codable {
    case hint
    case check_solution
    case reveal

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .hint:
            return "Hint"
        case .check_solution:
            return "Check Step"
        case .reveal:
            return "Reveal"
        }
    }
}

struct QueryResponse: Decodable {
    let verdict: String
    let response_type: String
    let message_is: String
}
