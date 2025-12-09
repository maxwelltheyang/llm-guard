import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.PBEKeySpec;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;
import java.security.spec.KeySpec;

public class SecureEncryption {

    private static final int ITERATION_COUNT = 65536;
    private static final int KEY_LENGTH = 256;
    private static final int GCM_TAG_LENGTH = 128;
    private static final int IV_LENGTH = 12; // Recommended length for GCM
    private static final String ALGORITHM = "AES/GCM/NoPadding";

    public static String encrypt(String message, String password) {
        try {
            // Generate a random IV using SecureRandom
            SecureRandom secureRandom = new SecureRandom();
            byte[] iv = new byte[IV_LENGTH];
            secureRandom.nextBytes(iv);
            GCMParameterSpec gcmSpec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);

            // Generate secret key from password using PBKDF2
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            KeySpec spec = new PBEKeySpec(password.toCharArray(), iv, ITERATION_COUNT, KEY_LENGTH);
            SecretKey secretKeyTmp = factory.generateSecret(spec);
            SecretKeySpec secretKey = new SecretKeySpec(secretKeyTmp.getEncoded(), "AES");

            // Initialize cipher in encrypt mode with secret key and IV
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, gcmSpec);

            // Encrypt the message
            byte[] encryptedBytes = cipher.doFinal(message.getBytes(StandardCharsets.UTF_8));

            // Combine IV and encrypted message
            byte[] encryptedMessageWithIv = new byte[iv.length + encryptedBytes.length];
            System.arraycopy(iv, 0, encryptedMessageWithIv, 0, iv.length);
            System.arraycopy(encryptedBytes, 0, encryptedMessageWithIv, iv.length, encryptedBytes.length);

            // Encode the combined byte array in Base64
            return Base64.getEncoder().encodeToString(encryptedMessageWithIv);
        } catch (Exception e) {
            throw new RuntimeException("Error occurred during encryption", e);
        }
    }

    public static void main(String[] args) {
        try {
            String message = "Hello, World!";
            String password = "securepassword";
            String encryptedMessage = encrypt(message, password);
            System.out.println("Encrypted Message: " + encryptedMessage);
        } catch (Exception e) {
            System.err.println("An error occurred during encryption: " + e.getMessage());
        }
    }
}
