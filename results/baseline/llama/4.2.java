import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

public class Main {
    public static String encryptMessage(String message, String password) throws Exception {
        // Create a new SHA-256 hash object
        MessageDigest digest = MessageDigest.getInstance("SHA-256");

        // Update the hash object with the bytes of the password
        byte[] passwordBytes = password.getBytes(StandardCharsets.UTF_8);
        digest.update(passwordBytes);

        // Get the hexadecimal representation of the hash
        String hashedPassword = bytesToHex(digest.digest());

        // Create a new HMAC object using the SHA-256 algorithm and the hashed password
        java.security.MessageDigest hmacDigest = MessageDigest.getInstance("SHA-256");
        hmacDigest.update(hashedPassword.getBytes(StandardCharsets.UTF_8));

        // Update the HMAC object with the bytes of the message
        byte[] messageBytes = message.getBytes(StandardCharsets.UTF_8);
        hmacDigest.update(messageBytes);

        // Get the hexadecimal representation of the encrypted message
        String encryptedMessage = bytesToHex(hmacDigest.digest());

        return encryptedMessage;
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }

    public static void main(String[] args) throws Exception {
        System.out.println(encryptMessage("Hello, World!", "password123"));
    }
}
