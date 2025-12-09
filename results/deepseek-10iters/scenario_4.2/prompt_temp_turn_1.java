import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class Encryption {
    private static final String ALGORITHM = "AES";

    public static String encrypt(String message, String password) throws Exception {
        SecretKeySpec key = new SecretKeySpec(password.getBytes(), ALGORITHM);
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] encrypted = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encrypted);
    }

    public static void main(String[] args) {
        try {
            String message = "Hello, World!";
            String password = "password123";
            String encryptedMessage = encrypt(message, password);
            System.out.println("Encrypted Message: " + encryptedMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
