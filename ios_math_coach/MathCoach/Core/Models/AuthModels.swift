import Foundation

struct RegisterRequest: Encodable {
    let email: String
    let password: String
}

struct LoginRequest: Encodable {
    let email: String
    let password: String
}

struct TokenResponse: Decodable {
    let access_token: String
    let token_type: String
}

struct MeResponse: Decodable {
    let id: String
    let email: String
}
