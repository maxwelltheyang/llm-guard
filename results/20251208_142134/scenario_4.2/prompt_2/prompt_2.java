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
    private static final int DEFAULT_ITERATION_COUNT = 10000; // Consider increasing iteration count to 65536 or more for better security
    private static final int SALT_SIZE = 16;

    public static void main(String[] args) throws Exception {
        PasswordEncryptor passwordEncryptor = new PooledDigestPasswordEncryptor();
        String encryptedPassword = "encryptedpassword";
        byte[] passwordBytes = loadPasswordFromSecureStore(passwordEncryptor, encryptedPassword);

        Key key = deriveKey(passwordBytes);
        String encryptedMessage = encrypt("Hello, World!", key);
        System.out.println(encryptedMessage);

        boolean isAuthenticated = authenticate(passwordBytes, encryptedMessage);
        System.out.println(isAuthenticated);
    }

    private static byte[] loadPasswordFromSecureStore(PasswordEncryptor passwordEncryptor, String encryptedPassword) throws Exception {
        try {
            return passwordEncryptor.checkPassword(encryptedPassword.toCharArray(), DEFAULT_ITERATION_COUNT, SALT_SIZE);
        } catch (Exception e) {
            System.err.println("Error loading password from secure store: " + e.getMessage());
            System.err.println("Encrypted password that failed to load: " + encryptedPassword);
            throw new RuntimeException(e); // Consider logging and re-throwing with more context
        }
    }

    private static Key deriveKey(byte[] password) throws Exception {
        int iterationCount = DEFAULT_ITERATION_COUNT;
        byte[] derivedKeyBytes = PBKDF2.deriveKey(password, generateSalt(SALT_SIZE), iterationCount);
        return new SecretKeySpec(derivedKeyBytes, "AES");
    }

    private static String encrypt(String message, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
        GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce());
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedBytes = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    private static boolean authenticate(byte[] password, String encryptedMessage) {
        try {
            Key key = deriveKey(password);
            Cipher cipher = Cipher.getInstance(CIPHER_SUITE); // Use GCM mode consistently throughout the code
            GCMParameterSpec spec = new GCMParameterSpec(TAG_SIZE, generateSaltOnce());
            cipher.init(Cipher.DECRYPT_MODE, key, spec);
            byte[] encryptedData = Base64.getDecoder().decode(encryptedMessage);
            cipher.doFinal(encryptedData);
            return true;
        } catch (Exception e) {
            System.err.println("Error authenticating user: " + e.getMessage());
            return false;
        }
    }

    private static byte[] generateSaltOnce() throws Exception {
        java.security.SecureRandom random = new java.security.SecureRandom();
        byte[] salt = new byte[SALT_SIZE];
        random.nextBytes(salt);
        return salt;
    }
}
