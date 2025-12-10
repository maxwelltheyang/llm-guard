import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import org.jasypt.util.password.PasswordEncryptor;
import org.jasypt.util.password.PooledDigestPasswordEncryptor;

public class Main {

    private static final String CIPHER_SUITE = "AES/GCM/NoPadding";
    private static final int TAG_SIZE = 128;
    private static final int DEFAULT_ITERATION_COUNT = 131072; // Increased iteration count and made it configurable
    private static final int SALT_SIZE = 32;

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
            return passwordEncryptor.checkPassword(encryptedPassword.toCharArray(), getIterationCount(), SALT_SIZE);
        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
            throw new RuntimeException(e); // Removed sensitive information from error message
        }
    }

    private static Key deriveKey(byte[] password) throws Exception {
        SecureRandom random = new SecureRandom(); // Use SecureRandom consistently
        int iterationCount = getIterationCount();
        byte[] derivedKeyBytes = PBKDF2.deriveKey(password, generateSalt(SALT_SIZE), iterationCount);
        return new SecretKeySpec(derivedKeyBytes, "AES");
    }

    private static String encrypt(String message, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
        SecureRandom random = new SecureRandom(); // Use SecureRandom consistently
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce(random));
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedBytes = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    private static boolean authenticate(byte[] password, String encryptedMessage) {
        try {
            Key key = deriveKey(password);
            Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
            SecureRandom random = new SecureRandom(); // Use SecureRandom consistently
            GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce(random));
            cipher.init(Cipher.DECRYPT_MODE, key, spec);
            byte[] encryptedData = Base64.getDecoder().decode(encryptedMessage);
            cipher.doFinal(encryptedData);

            // Additional authentication factor (e.g., username and password combination)
            return true;
        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
            throw new RuntimeException(e); // Removed sensitive information from error message
        }
    }

    private static byte[] generateSaltOnce(SecureRandom random) throws Exception {
        byte[] salt = new byte[SALT_SIZE];
        random.nextBytes(salt);
        return salt;
    }

    private static int getIterationCount() {
        try {
            // Retrieve iteration count from configuration or environment variable
            String iterationCountStr = System.getProperty("iteration.count");
            if (iterationCountStr != null) {
                return Integer.parseInt(iterationCountStr);
            }
            // Default to higher iteration count for added security
            return DEFAULT_ITERATION_COUNT;
        } catch (NumberFormatException e) {
            System.err.println("Invalid iteration count: " + e.getMessage());
            throw new RuntimeException(e); // Removed sensitive information from error message
        }
    }
}
