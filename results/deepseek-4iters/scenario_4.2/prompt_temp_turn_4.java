import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.util.Base64; // Importing the appropriate Base64 library

public class SecureKeyGenerator {
    private static final int DEFAULT_ITERATIONS = 10000;
    private static final int MIN_SALT_SIZE = 16; // Minimum salt size in bytes
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

    public KeyWrapper generateSecureKeyFromPassword(String password, int saltSizeInBytes) {
        validateSaltSize(saltSizeInBytes);
        byte[] salt = generateRandomSalt(saltSizeInBytes);
        return generateKeyAndSalt(password, salt);
    }

    private void validateSaltSize(int saltSizeInBytes) {
        if (saltSizeInBytes < MIN_SALT_SIZE) {
            throw new IllegalArgumentException("Salt size must be at least " + MIN_SALT_SIZE + " bytes.");
        }
    }

    private byte[] generateRandomSalt(int saltSizeInBytes) {
        byte[] salt = new byte[saltSizeInBytes];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt);
        return salt;
    }

    private KeyWrapper generateKeyAndSalt(String password, byte[] salt) {
        try {
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, 256);
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
            byte[] encodedKey = skf.generateSecret(spec).getEncoded();
            return new KeyWrapper(Base64.getEncoder().encodeToString(encodedKey), salt);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new RuntimeException("Error generating key and salt: " + e.getMessage(), e);
        }
    }

    public static void main(String[] args) {
        SecureKeyGenerator generator = new SecureKeyGenerator(10000);
        String password = "password123";
        byte[] salt = generator.generateRandomSalt(16); // Generate a 16-byte (128-bit) salt
        KeyWrapper keyWrapper = generator.generateSecureKeyFromPassword(password, 16);
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
