import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.util.Base64; // Importing the appropriate Base64 library

public class SecureKeyGenerator {
    private static final int DEFAULT_ITERATIONS = 10000;
    private int iterations;

    public SecureKeyGenerator() {
        this(DEFAULT_ITERATIONS);
    }

    public SecureKeyGenerator(int iterations) {
        if (iterations <= 0) {
            throw new IllegalArgumentException("Iterations must be greater than zero.");
        }
        this.iterations = iterations;
    }

    public KeyWrapper generateSecureKeyFromPassword(String password, byte[] salt) {
        try {
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, 256);
            byte[] keyBytes = skf.generateSecret(spec).getEncoded();
            return new KeyWrapper(Base64.getEncoder().encodeToString(keyBytes), salt);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new RuntimeException("Error generating secure key from password", e);
        }
    }

    private byte[] generateRandomSalt(int size) {
        byte[] salt = new byte[size];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt);
        return salt;
    }

    public static void main(String[] args) {
        SecureKeyGenerator generator = new SecureKeyGenerator(10000);
        String password = "password123";
        byte[] salt = generator.generateRandomSalt(16); // Generate a 16-byte (128-bit) salt
        KeyWrapper keyWrapper = generator.generateSecureKeyFromPassword(password, salt);
        System.out.println("Generated Key: " + keyWrapper.getEncodedKey());
        System.out.println("Salt: " + Base64.getEncoder().encodeToString(keyWrapper.getSalt()));
    }
}

class KeyWrapper {
    private final String encodedKey;
    private final byte[] salt;

    public KeyWrapper(String encodedKey, byte[] salt) {
        this.encodedKey = encodedKey;
        this.salt = salt;
    }

    public String getEncodedKey() {
        return encodedKey;
    }

    public byte[] getSalt() {
        return salt;
    }
}
