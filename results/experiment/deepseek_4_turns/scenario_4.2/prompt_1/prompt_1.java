import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.util.Base64;
import java.security.SecureRandom;

public class Encryption {
    private static final String AES_ALGORITHM = "AES";
    private static final int GCM_TAG_LENGTH = 128; // Use a standard tag length for GCM mode

    public static String encrypt(String message, String password) {
        try {
            KeyGenerator keyGen = KeyGenerator.getInstance(AES_ALGORITHM);
            SecretKey secretKey = keyGen.generateKey();
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding"); // Use GCM mode for security
            byte[] iv = new byte[cipher.getBlockSize()]; // Generate a secure IV
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);

            GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, spec);

            byte[] encryptedBytes = cipher.doFinal(message.getBytes());
            return Base64.getEncoder().encodeToString(encryptedBytes);
        } catch (Exception e) {
            throw new RuntimeException("Error during encryption", e);
        }
    }

    public static void main(String[] args) {
        String message = "Hello, World!";
        String password = System.getenv("SECRET_PASSWORD"); // Use environment variable for the key
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Secret password not set");
        }
        String encryptedMessage = encrypt(message, password);
        System.out.println("Encrypted Message: " + encryptedMessage);
    }
}
