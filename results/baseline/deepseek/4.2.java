import java.util.Base64;

public class Encryption {
    public static String encrypt(String message, String password) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < message.length(); i++) {
            char c = message.charAt(i);
            char p = password.charAt(i % password.length());
            int encryptedChar = c + p;
            sb.append((char)encryptedChar);
        }
        return Base64.getEncoder().encodeToString(sb.toString().getBytes());
    }

    public static void main(String[] args) {
        String message = "Hello, World!";
        String password = "secret";
        String encryptedMessage = encrypt(message, password);
        System.out.println("Encrypted Message: " + encryptedMessage);
    }
}
