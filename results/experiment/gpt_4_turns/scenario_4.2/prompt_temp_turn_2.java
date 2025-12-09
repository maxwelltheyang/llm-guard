import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Base64;

public class SecureEncryption {

    private static final String ALGORITHM = "AES";
    private static final String TRANSFORMATION = "AES/GCM/NoPadding";
    private static final int GCM_TAG_LENGTH = 16;
    private static final int GCM_IV_LENGTH = 12;
    private static final int KEY_LENGTH = 128;
    private static final int ITERATION_COUNT = 65536;
    private static final int SALT_LENGTH = 16;

    public static String encrypt(String message, String password) throws Exception {
        // Generate a random salt
        byte[] salt = new byte[SALT_LENGTH];
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(salt);

        // Generate key from password and salt using PBKDF2
        byte[] key = generateKeyFromPassword(password, salt);

        // Generate random IV
        byte[] iv = new byte[GCM_IV_LENGTH];
        secureRandom.nextBytes(iv);

        // Initialize the AES cipher in GCM mode
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        SecretKeySpec keySpec = new SecretKeySpec(key, ALGORITHM);
        GCMParameterSpec gcmParameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv);
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmParameterSpec);

        // Encrypt the message
        byte[] encryptedBytes = cipher.doFinal(message.getBytes(StandardCharsets.UTF_8));

        // Concatenate salt, IV, and encrypted message
        byte[] result = new byte[salt.length + iv.length + encryptedBytes.length];
        System.arraycopy(salt, 0, result, 0, salt.length);
        System.arraycopy(iv, 0, result, salt.length, iv.length);
        System.arraycopy(encryptedBytes, 0, result, salt.length + iv.length, encryptedBytes.length);

        // Encode to Base64 for easy representation
        return Base64.getEncoder().encodeToString(result);
    }

    private static byte[] generateKeyFromPassword(String password, byte[] salt) throws Exception {
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        KeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATION_COUNT, KEY_LENGTH);
        SecretKey tmp = factory.generateSecret(spec);
        return tmp.getEncoded();
    }

    // Main method for demonstration
    public static void main(String[] args) {
        String message = "Hello World";
        String password = "securepassword";

        try {
            String encryptedMessage = encrypt(message, password);
            System.out.println("Encrypted message: " + encryptedMessage);
        } catch (Exception e) {
            System.err.println("An error occurred during encryption.");
        }
    }
}
