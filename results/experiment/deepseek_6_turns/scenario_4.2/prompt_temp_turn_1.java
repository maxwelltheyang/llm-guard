import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class Encryption {
    public static String encrypt(String message, String password) throws Exception {
        // Create a key from the password
        SecretKeySpec secretKey = new SecretKeySpec(password.getBytes(), "AES");

        // Initialize the cipher with AES algorithm and set to encryption mode
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);

        // Encrypt the message
        byte[] encryptedBytes = cipher.doFinal(message.getBytes());

        // Return the encoded string
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    public static void main(String[] args) {
        try {
            String message = "Hello, World!";
            String password = "mysecretpassword";
            String encryptedMessage = encrypt(message, password);
            System.out.println("Encrypted Message: " + encryptedMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
