import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;

public class Main {
    public static String encryptMessage(String message, String password) throws NoSuchAlgorithmException {
        // Combine the password and salt to create a unique key for encryption
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = md.digest((message + password).getBytes(StandardCharsets.UTF_8));

        StringBuilder hexString = new StringBuilder();
        for (byte b : hashBytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }

        // Use the key to encrypt the message
        return new String(hashBytes).concat(message);
    }

    public static void main(String[] args) throws NoSuchAlgorithmException {
        System.out.println(encryptMessage("Hello, World!", "password123"));
    }
}
