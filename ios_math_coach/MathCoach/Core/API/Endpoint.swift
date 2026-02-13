import Foundation

enum Endpoint {
    case register
    case login
    case refresh
    case me
    case logout
    case query

    var path: String {
        switch self {
        case .register:
            return "/auth/register"
        case .login:
            return "/auth/login"
        case .refresh:
            return "/auth/refresh"
        case .me:
            return "/auth/me"
        case .logout:
            return "/auth/logout"
        case .query:
            return "/query"
        }
    }

    var method: String {
        switch self {
        case .me:
            return "GET"
        default:
            return "POST"
        }
    }
}
