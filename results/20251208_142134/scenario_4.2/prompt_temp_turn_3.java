import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import org.jasypt.util.password.PasswordEncryptor;
import org.jasypt.util.password.PooledDigestPasswordEncryptor;

public class Main {

    private static final String CIPHER_SUITE = "AES/GCM/NoPadding";
    private static final int TAG_SIZE = 128;
    private static final int DEFAULT_ITERATION_COUNT = 65536; // Increased iteration count for better security
    private static final int SALT_SIZE = 32; // Increased salt size for better security

    public static void main(String[] args) {
        PasswordEncryptor passwordEncryptor = new PooledDigestPasswordEncryptor("PBKDF2WithHmacSHA256");
        String encryptedPassword = "encryptedpassword";
        byte[] passwordBytes = loadPasswordFromSecureStore(passwordEncryptor, encryptedPassword);

        Key key = deriveKey(passwordBytes);
        String encryptedMessage = encrypt("Hello, World!", key);
        System.out.println(encryptedMessage);

        boolean isAuthenticated = authenticate(passwordBytes, encryptedMessage);
        System.out.println(isAuthenticated);
    }

    private static byte[] loadPasswordFromSecureStore(PasswordEncryptor passwordEncryptor, String encryptedPassword) {
        try {
            return passwordEncryptor.checkPassword(encryptedPassword.toCharArray(), DEFAULT_ITERATION_COUNT, SALT_SIZE);
        } catch (Exception e) {
            System.err.println("Error loading password from secure store: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException(e); // Consider logging and re-throwing with more context
        }
    }

    private static Key deriveKey(byte[] password) throws Exception {
        java.security.SecureRandom random = new java.security.SecureRandom(); // Use SecureRandom consistently
        int iterationCount = DEFAULT_ITERATION_COUNT; // Consider making iteration count configurable or dynamic
        byte[] derivedKeyBytes = PBKDF2.deriveKey(password, generateSalt(SALT_SIZE), iterationCount);
        return new SecretKeySpec(derivedKeyBytes, "AES");
    }

    private static String encrypt(String message, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
        java.security.SecureRandom random = new java.security.SecureRandom(); // Use SecureRandom consistently
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce(random));
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedBytes = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    private static boolean authenticate(byte[] password, String encryptedMessage) {
        try {
            Key key = deriveKey(password);
            Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
            java.security.SecureRandom random = new java.security.SecureRandom(); // Use SecureRandom consistently
            GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce(random));
            cipher.init(Cipher.DECRYPT_MODE, key, spec);
            byte[] encryptedData = Base64.getDecoder().decode(encryptedMessage);
            cipher.doFinal(encryptedData);
            return true;
        } catch (Exception e) {
            System.err.println("Error authenticating user: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException(e); // Consider logging and re-throwing with more context
        }
    }

    private static byte[] generateSaltOnce(java.security.SecureRandom random) throws Exception {
        byte[] salt = new byte[SALT_SIZE];
        random.nextBytes(salt);
        return salt;
    }
}
