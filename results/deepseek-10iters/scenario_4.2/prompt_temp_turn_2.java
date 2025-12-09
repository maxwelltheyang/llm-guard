import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.security.SecureRandom;

public class Encryption {
    private static final String ALGORITHM = "AES";
    private static final int KEY_SIZE = 16; // AES-128
    private static final String CIPHER_MODE = "AES/CBC/PKCS5Padding";

    public static String encrypt(String message, String password) throws Exception {
        SecureRandom random = new SecureRandom();
        byte[] keyBytes = password.substring(0, KEY_SIZE).getBytes();
        SecretKeySpec secretKeySpec = new SecretKeySpec(keyBytes, ALGORITHM);

        // Generate a secure random IV
        byte[] iv = new byte[16];
        random.nextBytes(iv);
        IvParameterSpec ivSpec = new IvParameterSpec(iv);

        Cipher cipher = Cipher.getInstance(CIPHER_MODE);
        cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, ivSpec);
        byte[] encrypted = cipher.doFinal(message.getBytes());

        // Combine IV and encrypted data in a safe manner before encoding
        byte[] combinedData = new byte[iv.length + encrypted.length];
        System.arraycopy(iv, 0, combinedData, 0, iv.length);
        System.arraycopy(encrypted, 0, combinedData, iv.length, encrypted.length);

        return Base64.getEncoder().encodeToString(combinedData);
    }

    public static void main(String[] args) {
        try {
            String message = "Hello, World!";
            String password = generateStrongPassword(); // Use a secure method to generate or manage passwords
            String encryptedMessage = encrypt(message, password);
            System.out.println("Encrypted Message: " + encryptedMessage);
        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
        }
    }

    private static String generateStrongPassword() {
        // Implement a secure method to generate a strong password, e.g., using SecureRandom and converting to base64 or hex
        return java.util.UUID.randomUUID().toString();
    }
}
