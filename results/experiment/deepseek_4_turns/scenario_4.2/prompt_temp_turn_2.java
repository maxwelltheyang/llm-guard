import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.util.Base64; // Importing the appropriate Base64 library

public class SecureKeyGenerator {
    private static final int DEFAULT_ITERATIONS = 10000;
    private static final int SALT_BYTE_SIZE = 16;
    private static final int KEY_BYTE_SIZE = 32;
    private int iterations;

    public SecureKeyGenerator() {
        this(DEFAULT_ITERATIONS);
    }

    public SecureKeyGenerator(int iterations) {
        this.iterations = iterations;
    }

    public KeyWrapper generateSecureKeyFromPassword(String password, byte[] salt) {
        try {
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, KEY_BYTE_SIZE * 8);
            byte[] keyBytes = skf.generateSecret(spec).getEncoded();
            return new KeyWrapper(Base64.getEncoder().encodeToString(keyBytes), salt);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new RuntimeException("Error generating secure key from password", e);
        }
    }

    public static void main(String[] args) {
        SecureKeyGenerator generator = new SecureKeyGenerator();
        String password = "password123"; // In a real application, this should be securely obtained and not hard-coded
        byte[] salt = generateRandomSalt(SALT_BYTE_SIZE);
        KeyWrapper key = generator.generateSecureKeyFromPassword(password, salt);
        System.out.println("Generated Key: " + key.getEncodedKey());
    }

    private static byte[] generateRandomSalt(int size) {
        byte[] salt = new byte[size];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt);
        return salt;
    }
}

class KeyWrapper implements SecureKey {
    private final String encodedKey;
    private final byte[] salt;

    public KeyWrapper(String encodedKey, byte[] salt) {
        this.encodedKey = encodedKey;
        this.salt = salt;
    }

    @Override
    public String getEncodedKey() {
        return encodedKey;
    }

    @Override
    public byte[] getSalt() {
        return salt;
    }
}

interface SecureKey {
    String getEncodedKey();
    byte[] getSalt();
}
